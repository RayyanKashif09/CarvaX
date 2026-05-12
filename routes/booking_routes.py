from datetime import date, datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.booking import Booking
from models.vehicle import Vehicle
from models.user import User

booking_bp = Blueprint('bookings', __name__)


@booking_bp.route('/', methods=['GET'])
@jwt_required()
def get_bookings():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.role == 'admin':
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    else:
        bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()

    return jsonify({'bookings': [b.to_dict() for b in bookings]})


@booking_bp.route('/create', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()

    if not data or not all(k in data for k in ('vehicle_id', 'start_date', 'end_date')):
        return jsonify({'error': 'vehicle_id, start_date, end_date are required'}), 400

    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    if vehicle.status != 'available':
        return jsonify({'error': 'Vehicle is not available'}), 409

    try:
        start = date.fromisoformat(data['start_date'])
        end = date.fromisoformat(data['end_date'])
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if end <= start:
        return jsonify({'error': 'End date must be after start date'}), 400
    if start < date.today():
        return jsonify({'error': 'Start date cannot be in the past'}), 400

    total_days = (end - start).days
    total_amount = total_days * float(vehicle.price_per_day)

    booking = Booking(
        user_id=user.id,
        vehicle_id=vehicle.id,
        start_date=start,
        end_date=end,
        total_days=total_days,
        total_amount=total_amount,
        status='active',
    )
    vehicle.status = 'rented'

    db.session.add(booking)
    db.session.commit()

    return jsonify({'message': 'Booking created', 'booking': booking.to_dict()}), 201


@booking_bp.route('/history', methods=['GET'])
@jwt_required()
def booking_history():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]})


@booking_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    booking = Booking.query.get_or_404(booking_id)

    if user.role != 'admin' and booking.user_id != int(user_id):
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({'booking': booking.to_dict()})


@booking_bp.route('/return/<int:booking_id>', methods=['PUT'])
@jwt_required()
def return_vehicle(booking_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    booking = Booking.query.get_or_404(booking_id)

    if user.role != 'admin' and booking.user_id != int(user_id):
        return jsonify({'error': 'Access denied'}), 403

    if booking.status not in ('active', 'pending'):
        return jsonify({'error': 'This booking cannot be returned'}), 400

    booking.status = 'completed'
    vehicle = Vehicle.query.get(booking.vehicle_id)
    if vehicle:
        vehicle.status = 'available'

    db.session.commit()
    return jsonify({'message': 'Vehicle returned successfully', 'booking': booking.to_dict()})


@booking_bp.route('/cancel/<int:booking_id>', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    booking = Booking.query.get_or_404(booking_id)

    if user.role != 'admin' and booking.user_id != int(user_id):
        return jsonify({'error': 'Access denied'}), 403

    if booking.status not in ('pending', 'active'):
        return jsonify({'error': 'Cannot cancel this booking'}), 400

    booking.status = 'cancelled'
    vehicle = Vehicle.query.get(booking.vehicle_id)
    if vehicle and vehicle.status == 'rented':
        vehicle.status = 'available'

    db.session.commit()
    return jsonify({'message': 'Booking cancelled', 'booking': booking.to_dict()})
