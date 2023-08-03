from flask_sqlalchemy import SQLAlchemy
from main import app
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import bcrypt
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
db = SQLAlchemy(app)
class Quotation(db.Model):
    __tablename__ = "quotations"

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    quotation_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    
    driver = relationship("User", foreign_keys=[driver_id],backref="driver_quotations",overlaps="quotations_as_driver")
    passenger = relationship("User", foreign_keys=[passenger_id],backref="passenger_quotations",overlaps="quotations_as_passenger")
    rides = relationship("Ride", back_populates="quotation")    

    def __init__(self, driver_id, passenger_id, trip_id, quotation_amount,status):
        self.driver_id = driver_id
        self.passenger_id = passenger_id
        self.trip_id = trip_id
        self.quotation_amount = quotation_amount
        self.status = status

class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)

    quotations = relationship("Quotation",backref="trip_quotations",overlaps="quotations_trip")
    driver = relationship("User", foreign_keys=[driver_id], backref="trips_as_driver_rel",overlaps="rides_as_driver")
    passenger = relationship("User", foreign_keys=[passenger_id], backref="trips_as_passenger_rel",overlaps="rides_as_passenger")

    def __init__(self, driver_id, passenger_id, from_location, to_location):
        self.driver_id = driver_id
        self.passenger_id = passenger_id
        self.from_location = from_location
        self.to_location = to_location

class Ride(db.Model):
    __tablename__ = 'rides'
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False,default='Pending')
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'))
    quotation = relationship('Quotation', back_populates='rides',foreign_keys=[quotation_id])
    driver = relationship("User", foreign_keys=[driver_id], backref="rides_as_driver_rel")
    passenger = relationship("User", foreign_keys=[passenger_id], backref="rides_as_passenger_rel")

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    
    driver = relationship("User", foreign_keys=[driver_id])
    passenger = relationship("User", foreign_keys=[passenger_id])
    trip = relationship("Trip")
    quotation = relationship("Quotation")

    def __init__(self, passenger_id, driver_id, trip_id, quotation_id, message):
        self.passenger_id = passenger_id
        self.driver_id = driver_id
        self.trip_id = trip_id
        self.quotation_id = quotation_id
        self.message = message

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)
    rides_as_driver = relationship("Trip", foreign_keys="Trip.driver_id", backref="driver_rel")
    rides_as_passenger = relationship("Trip", foreign_keys="Trip.passenger_id", backref="passenger_rel")
    
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)

    def generate_reset_token(self):
            self.reset_token = secrets.token_hex(20)
            self.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            return self.reset_token


    def __init__(self, username, password, user_type, email):
        self.username = username
        self.password = self.generate_password_hash(password)  # Hash the password
        self.email = email
        self.user_type = user_type

    def generate_password_hash(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))






