import requests
from datetime import datetime
from database import app, db, AirQualityData, Location
from apscheduler.schedulers.background import BackgroundScheduler

def fetch_airly_data(api_key, location_id):
    headers = {
        "Accept": "application/json",
        "apikey": api_key
    }
   
    url_location = f"https://api.airly.eu/v2/installations/location={location_id}"
    response = requests.get(url_location, headers=headers)
    data = response.json()

    location_data = data['location']
    address_data = data['address']

    location = Location.query.get(data['id'])
    if not location:
        location = Location(
            id=data['id'],
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            country=address_data['country'],
            city=address_data['city'],
            street=address_data.get('street'),
            number=address_data.get('number'),
            elevation=data.get('elevation'),
        )
        db.session.add(location)
        db.session.commit()

    
    url_measurements  = f"https://api.airly.eu/v2/measurements/location={location_id}"
    response_measurements = requests.get(url_measurements, headers=headers)
    data_measurements = response_measurements.json()

    air_quality_data = data_measurements['current']['values']
    timestamp = datetime.strptime(data_measurements['current']['fromDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")

    air_quality = AirQualityData(
        timestamp=timestamp,
        pm1=next(item for item in air_quality_data if item["name"] == "PM1")['value'],
        pm25=next(item for item in air_quality_data if item["name"] == "PM25")['value'],
        pm10=next(item for item in air_quality_data if item["name"] == "PM10")['value'],
        pressure=next(item for item in air_quality_data if item["name"] == "PRESSURE")['value'],
        humidity=next(item for item in air_quality_data if item["name"] == "HUMIDITY")['value'],
        temperature=next(item for item in air_quality_data if item["name"] == "TEMPERATURE")['value'],
        location_id=location.id
    )

    db.session.add(air_quality)
    db.session.commit()

def start_scheduler(api_key, location_ids):
    scheduler = BackgroundScheduler()
    for location_id in location_ids:
        scheduler.add_job(fetch_airly_data, 'interval', hours=1, args=[api_key, location_id])
    scheduler.start()

# Tutaj lokalizacje (na razie 4-ry, pytanie czy więcej)
locations = [86934, 32932, 35894, 3478] #[Studencka-Kraków, Chmielna-Warszawa, Mennicza-Wrocław, Strajku Dokerów-Gdańsk]

# Uruchomienie cyklicznego taska co godzinę -> można dodać podawanie listy kluczów API, wiadomo ale to później
if __name__ == '__main__':
    with app.app_context():
        start_scheduler(api_key='Y7ib9CyZfvqgcPXxEnSUtRkps8TmSIOb', location_ids=locations)
    app.run(debug=True)