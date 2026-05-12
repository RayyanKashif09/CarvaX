"""Run this once after setting up the database to add sample vehicles."""
from app import create_app
from models import db
from models.vehicle import Vehicle

SAMPLE_VEHICLES = [
    dict(name='Model S Plaid', brand='Tesla', model='Model S', year=2024, category='Electric',
         description='The fastest production sedan ever made. 1,020 hp, 0-60 in 1.99s.',
         price_per_day=299.00),
    dict(name='911 Carrera', brand='Porsche', model='911', year=2023, category='Sports',
         description='Iconic rear-engine sports car with 379hp flat-six engine.',
         price_per_day=349.00),
    dict(name='Range Rover Sport', brand='Land Rover', model='Range Rover Sport', year=2024,
         category='SUV', description='Luxurious off-road capable SUV with premium interior.',
         price_per_day=199.00),
    dict(name='S-Class Executive', brand='Mercedes-Benz', model='S-Class', year=2023,
         category='Luxury', description='The pinnacle of luxury motoring. Massaging seats, MBUX.',
         price_per_day=249.00),
    dict(name='Civic Sport', brand='Honda', model='Civic', year=2024, category='Sedan',
         description='Reliable, fuel-efficient and sporty compact sedan.',
         price_per_day=69.00),
    dict(name='Mustang GT', brand='Ford', model='Mustang', year=2023, category='Sports',
         description='5.0L V8 Coyote engine. Pure American muscle.',
         price_per_day=149.00),
    dict(name='Cayenne GTS', brand='Porsche', model='Cayenne', year=2024, category='SUV',
         description='Performance SUV with 473hp twin-turbo V8.',
         price_per_day=289.00),
    dict(name='Model 3 Standard', brand='Tesla', model='Model 3', year=2024, category='Electric',
         description='The world\'s bestselling electric car. Clean, fast, and fun.',
         price_per_day=129.00),
]


def seed():
    app = create_app()
    with app.app_context():
        if Vehicle.query.count() > 0:
            print('Vehicles already seeded.')
            return
        for data in SAMPLE_VEHICLES:
            v = Vehicle(**data)
            db.session.add(v)
        db.session.commit()
        print(f'Seeded {len(SAMPLE_VEHICLES)} vehicles.')


if __name__ == '__main__':
    seed()
