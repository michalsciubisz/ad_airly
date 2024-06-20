import requests
from datetime import datetime
from database import app, db, Location, DustMeasurements, GasMeasurements, AQIIndicator
from apscheduler.schedulers.background import BackgroundScheduler

def fetch_airly_data(api_key, location_id):
    headers = {
        "Accept": "application/json",
        "apikey": api_key
    }
    url_measurements  = f"https://api.airly.eu/v2/measurements/location?locationId={location_id}"
    try:
        response_measurements = requests.get(url_measurements, headers=headers)
        response_measurements.raise_for_status()  # Raise error for non-200 status codes
        data_measurements = response_measurements.json()
        
        air_quality_data = data_measurements['current']['values']
        indexes_data = data_measurements['current']['indexes'][0]
        timestamp = datetime.strptime(data_measurements['current']['fromDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")

        location = Location.query.get(location_id)
        if not location:
            #Dodanie danych jeśli ich nie ma jeszcze w bazie danych
            url_location = f"https://api.airly.eu/v2/installations/location?locationId={location_id}"
            response_location = requests.get(url_location, headers=headers)
            response_location.raise_for_status()  # Gdyby był brak połączenia przy podejściu do API
            data_location = response_location.json()

            location_data = data_location['location']
            address_data = data_location['address']
            
            location = Location(
                id=data_location['id'],
                latitude=location_data['latitude'],
                longitude=location_data['longitude'],
                country=address_data['country'],
                city=address_data['city'],
                street=address_data['street'],
                number=address_data['number'],
                elevation=data_location['elevation'],
            )
            db.session.add(location)

        dust_measurement = DustMeasurements(
            timestamp=timestamp,
            pm25 = next(item for item in air_quality_data if item["name"] == "PM25")['value'],
            pm10 = next(item for item in air_quality_data if item["name"] == "PM10")['value'],
            location_id=location.id
        )
        db.session.add(dust_measurement)

        gas_measurement = GasMeasurements(
            timestamp=timestamp,
            no2 = next(item for item in air_quality_data if item["name"] == "NO2")['value'],
            o3 = next(item for item in air_quality_data if item["name"] == "O3")['value'],
            so2 = next(item for item in air_quality_data if item["name"] == "SO2")['value'],
            co = next(item for item in air_quality_data if item["name"] == "CO")['value'],
            location_id=location.id
        )
        db.session.add(gas_measurement)

        aqi_measurement = AQIIndicator(
            index_name = indexes_data["name"],
            indicator_value = indexes_data["value"],
            level = indexes_data['level'],
            description = indexes_data['description'],
            advice = indexes_data['advice'],
            dust_measurement_id = dust_measurement.id,
            gas_measurement_id = gas_measurement.id
        )
        db.session.add(aqi_measurement)

        db.session.commit()
        print(f"Successfully fetched and saved data for locationId {location_id}")

    except Exception as e:
        db.session.rollback()
        print(f"Error processing data for locationId {location_id}: {e}")

def start_scheduler(api_key, location_ids):
    scheduler = BackgroundScheduler()
    for location_id in location_ids:
        scheduler.add_job(lambda: fetch_airly_data(api_key, location_id), 'interval', hours=1)
    scheduler.start()

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

# Tutaj lokalizacje (na razie 5, pytanie czy więcej)
locations = [37, 24, 8, 19, 45]  #[Gdańsk, Radom, Wrocław, Kraków, Olsztyn]

# Uruchomienie cyklicznego taska co godzinę -> można dodać podawanie listy kluczów API, wiadomo ale to później
if __name__ == '__main__':
    with app.app_context():
        start_scheduler(api_key='Y7ib9CyZfvqgcPXxEnSUtRkps8TmSIOb', location_ids=locations)