from models import db
from datetime import datetime


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    category = db.Column(db.String(50), default='Sedan')
    description = db.Column(db.Text)
    price_per_day = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='available')
    image = db.Column(db.String(255), default='default_car.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='vehicle', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'category': self.category,
            'description': self.description,
            'price_per_day': float(self.price_per_day),
            'status': self.status,
            'image': self.image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
