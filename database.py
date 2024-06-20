from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Do połączenia trzeba używać albo VPNa albo być w sieci AGH
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://michals1:ZDg8L4NMGhAVDkGV@mysql.agh.edu.pl:3306/michals1'
db = SQLAlchemy(app)

#Utworzenie dwóch tabeli
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=True)
    number = db.Column(db.String(10), nullable=True)
    elevation = db.Column(db.Float, nullable=True)
    air_quality_data = db.relationship('AirQualityData', backref='location', lazy=True)

class AirQualityData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    pm1 = db.Column(db.Float, nullable=False)
    pm25 = db.Column(db.Float, nullable=False)
    pm10 = db.Column(db.Float, nullable=False)
    aqi = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

#Wysłanie tabeli do bazy danych
db.create_all()

if __name__ == '__main__':
    app.run(debug=True)