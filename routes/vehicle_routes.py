import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db
from models.vehicle import Vehicle
from models.user import User

vehicle_bp = Blueprint('vehicles', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def require_admin():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None, jsonify({'error': 'Admin access required'}), 403
    return user, None, None


@vehicle_bp.route('/', methods=['GET'])
def get_vehicles():
    status = request.args.get('status', 'available')
    category = request.args.get('category')
    query = Vehicle.query

    if status != 'all':
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)

    vehicles = query.order_by(Vehicle.created_at.desc()).all()
    return jsonify({'vehicles': [v.to_dict() for v in vehicles]})


@vehicle_bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify({'vehicle': vehicle.to_dict()})


@vehicle_bp.route('/search', methods=['GET'])
def search_vehicles():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'vehicles': []})

    vehicles = Vehicle.query.filter(
        (Vehicle.name.ilike(f'%{q}%')) |
        (Vehicle.brand.ilike(f'%{q}%')) |
        (Vehicle.model.ilike(f'%{q}%')) |
        (Vehicle.category.ilike(f'%{q}%'))
    ).all()

    return jsonify({'vehicles': [v.to_dict() for v in vehicles]})


@vehicle_bp.route('/add', methods=['POST'])
@jwt_required()
def add_vehicle():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    image_filename = 'default_car.jpg'
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(upload_path)
            image_filename = filename

    data = request.form if request.form else request.get_json() or {}

    if not all(k in data for k in ('name', 'brand', 'model', 'price_per_day')):
        return jsonify({'error': 'Name, brand, model, and price_per_day are required'}), 400

    vehicle = Vehicle(
        name=data['name'],
        brand=data['brand'],
        model=data['model'],
        year=int(data.get('year', 0)) or None,
        category=data.get('category', 'Sedan'),
        description=data.get('description', ''),
        price_per_day=float(data['price_per_day']),
        status=data.get('status', 'available'),
        image=image_filename,
    )
    db.session.add(vehicle)
    db.session.commit()

    return jsonify({'message': 'Vehicle added', 'vehicle': vehicle.to_dict()}), 201


@vehicle_bp.route('/update/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def update_vehicle(vehicle_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.form if request.form else request.get_json() or {}

    for field in ('name', 'brand', 'model', 'category', 'description', 'status'):
        if field in data:
            setattr(vehicle, field, data[field])
    if 'year' in data:
        vehicle.year = int(data['year']) if data['year'] else None
    if 'price_per_day' in data:
        vehicle.price_per_day = float(data['price_per_day'])

    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(upload_path)
            vehicle.image = filename

    db.session.commit()
    return jsonify({'message': 'Vehicle updated', 'vehicle': vehicle.to_dict()})


@vehicle_bp.route('/delete/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': 'Vehicle deleted'})
