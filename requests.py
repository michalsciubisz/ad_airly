import urllib.request
import json
from datetime import datetime
from database import app, db, Location, DustMeasurements, GasMeasurements, AQIIndicator
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import sessionmaker


def fetch_airly_data(api_key, location_id, Session):
    session = None
    try:
        with app.app_context():
            Session = sessionmaker(bind=db.engine)
            print('Fetching data for location:', location_id)
            headers = {
                "Accept": "application/json",
                "apikey": api_key
            }
            url_measurements = f"https://airapi.airly.eu/v2/measurements/location?locationId={location_id}"
            print('Requesting URL:', url_measurements)
            response_measurements = urllib.request.Request(url_measurements, headers=headers)

            with urllib.request.urlopen(response_measurements) as response:
                if response.status != 200:
                    raise Exception(f"Non-200 status code: {response.status}")
                data_measurements = json.load(response)

            air_quality_data = data_measurements['current']['values']
            indexes_data = data_measurements['current']['indexes'][0]
            timestamp = datetime.now() #Biore obecny bo to nie ma znaczenia

            session = Session()
            location = session.query(Location).filter_by(id=location_id).first()
            if not location:
                # Dodanie jeśli lokalizacja jeszcze nie istnieje
                url_location = f"https://airapi.airly.eu/v2/installations/location?locationId={location_id}"
                response_location = urllib.request.Request(url_location, headers=headers)

                with urllib.request.urlopen(response_location) as response:
                    if response.status != 200:
                        raise Exception(f"Non-200 status code: {response.status}")
                    data_location = json.load(response)

                location_data = data_location['location']
                address_data = data_location['address']

                location = Location(
                    id=data_location['id'],
                    latitude=location_data['latitude'],
                    longitude=location_data['longitude'],
                    country=address_data['country'],
                    city=address_data['city'],
                    street=address_data['street'],
                    number=address_data.get('number'), #.get radzi sobie z przypadkiem braku tej informacji, pozostałe są zawsze
                    elevation=data_location['elevation'],
                )
                session.add(location)
                session.commit() #Commit żeby mieć dostęp dalej

            dust_measurement = DustMeasurements(
                timestamp=timestamp,
                pm25=next((item['value'] for item in air_quality_data if item["name"] == "PM25"),None),
                pm10=next((item['value'] for item in air_quality_data if item["name"] == "PM10"),None),
                location_id=location.id
            )
            session.add(dust_measurement)

            gas_measurement = GasMeasurements(
                timestamp=timestamp,
                no2=next((item['value'] for item in air_quality_data if item["name"] == "NO2"),None),
                o3=next((item['value'] for item in air_quality_data if item["name"] == "O3"),None),
                so2=next((item['value'] for item in air_quality_data if item["name"] == "SO2"),None),
                co=next((item['value'] for item in air_quality_data if item["name"] == "CO"),None),
                location_id=location.id
            )
            session.add(gas_measurement)
            session.commit() #Commit żeby dostać .id w aqi pomiarze
            
            aqi_measurement = AQIIndicator(
                index_name=indexes_data["name"],
                indicator_value=indexes_data["value"],
                level=indexes_data['level'],
                description=indexes_data['description'],
                advice=indexes_data['advice'],
                dust_measurement_id=dust_measurement.id,
                gas_measurement_id=gas_measurement.id
            )
            session.add(aqi_measurement)
            session.commit()
            print(f"Successfully fetched and saved data for locationId {location_id}")

    except urllib.error.HTTPError as e: #Error ze złym id dla requestu
        if e.code == 404:
            print(f"Location ID {location_id} not found: {e}")
        else:
            if session:
                session.rollback()
            print(f"Error processing data for locationId {location_id}: {e}")

    except Exception as e:
        if session:
            session.rollback()
        print(f"Error processing data for locationId {location_id}: {e}")

    finally:
        if session:
            session.close()


def start_scheduler(api_key, location_ids):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        scheduler = BackgroundScheduler()
        for location_id in location_ids:
            scheduler.add_job(lambda loc_id=location_id: fetch_airly_data(api_key, loc_id, Session), 'interval', seconds=10)
        scheduler.start()

        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()

# Uruchomienie cyklicznego taska co godzinę -> można dodać podawanie listy kluczów API, wiadomo ale to później
if __name__ == '__main__':
    # Tutaj lokalizacje (na razie 5, pytanie czy więcej)
    locations = [37, 24, 8, 19, 45]  #[Gdańsk, Radom, Wrocław, Kraków, Olsztyn]
    start_scheduler(api_key='Y7ib9CyZfvqgcPXxEnSUtRkps8TmSIOb', location_ids=locations)