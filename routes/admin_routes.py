from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.booking import Booking
from models.payment import Payment

admin_bp = Blueprint('admin', __name__)


def require_admin(user_id):
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None
    return user


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    if not require_admin(user_id):
        return jsonify({'error': 'Admin access required'}), 403

    total_users = User.query.filter_by(role='user').count()
    total_vehicles = Vehicle.query.count()
    available_vehicles = Vehicle.query.filter_by(status='available').count()
    rented_vehicles = Vehicle.query.filter_by(status='rented').count()
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status='active').count()
    completed_bookings = Booking.query.filter_by(status='completed').count()

    revenue_result = db.session.query(func.sum(Payment.amount)).filter_by(payment_status='completed').scalar()
    total_revenue = float(revenue_result or 0)

    recent_bookings = (
        Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    )

    vehicle_stats = db.session.query(
        Vehicle.category,
        func.count(Vehicle.id).label('count')
    ).group_by(Vehicle.category).all()

    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_vehicles': total_vehicles,
            'available_vehicles': available_vehicles,
            'rented_vehicles': rented_vehicles,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'completed_bookings': completed_bookings,
            'total_revenue': total_revenue,
        },
        'recent_bookings': [b.to_dict() for b in recent_bookings],
        'vehicle_stats': [{'category': s[0], 'count': s[1]} for s in vehicle_stats],
    })


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = get_jwt_identity()
    if not require_admin(user_id):
        return jsonify({'error': 'Admin access required'}), 403

    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]})


@admin_bp.route('/users/<int:uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    user_id = get_jwt_identity()
    if not require_admin(user_id):
        return jsonify({'error': 'Admin access required'}), 403

    if int(user_id) == uid:
        return jsonify({'error': 'Cannot delete your own account'}), 400

    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})


@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_all_bookings():
    user_id = get_jwt_identity()
    if not require_admin(user_id):
        return jsonify({'error': 'Admin access required'}), 403

    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]})
