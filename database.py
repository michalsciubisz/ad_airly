from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Do połączenia trzeba używać VPNa albo być w sieci AGH
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://michals1:ZDg8L4NMGhAVDkGV@mysql.agh.edu.pl:3306/michals1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Utworzenie czterech tabeli
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(10), nullable=True)
    elevation = db.Column(db.Float, nullable=True)
    dust_measurements = db.relationship('DustMeasurements', backref='location', lazy=True)
    gas_measurements = db.relationship('GasMeasurements', backref='location', lazy=True)

class DustMeasurements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    pm10 = db.Column(db.Float, nullable=True)
    pm25 = db.Column(db.Float, nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

class GasMeasurements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    no2 = db.Column(db.Float, nullable=True)
    o3 = db.Column(db.Float, nullable=True)
    so2 = db.Column(db.Float, nullable=True)
    co = db.Column(db.Float, nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

class AQIIndicator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index_name = db.Column(db.String(50), nullable=False)
    indicator_value = db.Column(db.Float, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    advice = db.Column(db.String(150), nullable=False)
    dust_measurement_id = db.Column(db.Integer, db.ForeignKey('dust_measurements.id'))
    gas_measurement_id = db.Column(db.Integer, db.ForeignKey('gas_measurements.id'))


#Wysłanie tabeli do bazy danych
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)