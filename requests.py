import requests
from datetime import datetime
from database import db, AirQualityData, Location

def fetch_airly_data(api_key, location_id):
    url = f"https://api.airly.eu/v2/measurements/installation?installationId={location_id}"
    headers = {
        "Accept": "application/json",
        "apikey": api_key
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    location_data = data['location']
    address_data = data['address']
    sponsor_data = data['sponsor']

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
            sponsor_id=sponsor_data.get('id'),
            sponsor_name=sponsor_data.get('name'),
            sponsor_description=sponsor_data.get('description'),
            sponsor_logo=sponsor_data.get('logo'),
            sponsor_link=sponsor_data.get('link'),
            display_address1=address_data.get('displayAddress1'),
            display_address2=address_data.get('displayAddress2')
        )
        db.session.add(location)
        db.session.commit()

    air_quality_data = data['current']['values']
    timestamp = datetime.strptime(data['current']['fromDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")

    air_quality = AirQualityData(
        timestamp=timestamp,
        pm1=next(item for item in air_quality_data if item["name"] == "PM1")['value'],
        pm25=next(item for item in air_quality_data if item["name"] == "PM25")['value'],
        pm10=next(item for item in air_quality_data if item["name"] == "PM10")['value'],
        aqi=next(item for item in air_quality_data if item["name"] == "AQI")['value'],
        pressure=next(item for item in air_quality_data if item["name"] == "PRESSURE")['value'],
        humidity=next(item for item in air_quality_data if item["name"] == "HUMIDITY")['value'],
        temperature=next(item for item in air_quality_data if item["name"] == "TEMPERATURE")['value'],
        location_id=location.id
    )

    db.session.add(air_quality)
    db.session.commit()