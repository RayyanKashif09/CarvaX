from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.payment import Payment
from models.booking import Booking
from models.user import User

payment_bp = Blueprint('payments', __name__)


@payment_bp.route('/', methods=['GET'])
@jwt_required()
def get_payments():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role == 'admin':
        payments = Payment.query.order_by(Payment.created_at.desc()).all()
    else:
        booking_ids = [b.id for b in Booking.query.filter_by(user_id=user.id).all()]
        payments = Payment.query.filter(Payment.booking_id.in_(booking_ids)).order_by(Payment.created_at.desc()).all()

    return jsonify({'payments': [p.to_dict() for p in payments]})


@payment_bp.route('/create', methods=['POST'])
@jwt_required()
def create_payment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()

    if not data or 'booking_id' not in data:
        return jsonify({'error': 'booking_id is required'}), 400

    booking = Booking.query.get(data['booking_id'])
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if user.role != 'admin' and booking.user_id != int(user_id):
        return jsonify({'error': 'Access denied'}), 403

    if booking.payment:
        return jsonify({'error': 'Payment already exists for this booking'}), 409

    payment = Payment(
        booking_id=booking.id,
        amount=float(data.get('amount', booking.total_amount)),
        payment_method=data.get('payment_method', 'cash'),
        payment_status='completed',
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({'message': 'Payment recorded', 'payment': payment.to_dict()}), 201


@payment_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    payment = Payment.query.get_or_404(payment_id)
    booking = Booking.query.get(payment.booking_id)

    if user.role != 'admin' and booking.user_id != int(user_id):
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({'payment': payment.to_dict()})
