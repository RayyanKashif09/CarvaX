import os
from flask import Flask, render_template, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db

jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    from routes.auth_routes import auth_bp
    from routes.vehicle_routes import vehicle_bp
    from routes.booking_routes import booking_bp
    from routes.payment_routes import payment_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vehicle_bp, url_prefix='/api/vehicles')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Page routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/signup')
    def signup_page():
        return render_template('signup.html')

    @app.route('/forgot-password')
    def forgot_password_page():
        return render_template('forgot_password.html')

    @app.route('/reset-password')
    def reset_password_page():
        return render_template('reset_password.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    @app.route('/admin')
    def admin_page():
        return render_template('admin.html')

    @app.route('/vehicles')
    def vehicles_page():
        return render_template('vehicles.html')

    @app.route('/vehicles/<int:vehicle_id>')
    def vehicle_detail_page(vehicle_id):
        return render_template('vehicle_detail.html', vehicle_id=vehicle_id)

    @app.route('/vehicles/add')
    def add_vehicle_page():
        return render_template('add_vehicle.html')

    @app.route('/vehicles/edit/<int:vehicle_id>')
    def edit_vehicle_page(vehicle_id):
        return render_template('edit_vehicle.html', vehicle_id=vehicle_id)

    @app.route('/booking/<int:vehicle_id>')
    def booking_page(vehicle_id):
        return render_template('booking.html', vehicle_id=vehicle_id)

    @app.route('/payment/<int:booking_id>')
    def payment_page(booking_id):
        return render_template('payment.html', booking_id=booking_id)

    @app.route('/history')
    def history_page():
        return render_template('booking_history.html')

    @app.route('/profile')
    def profile_page():
        return render_template('profile.html')

    @app.route('/search')
    def search_page():
        return render_template('search.html')

    @app.route('/return/<int:booking_id>')
    def return_vehicle_page(booking_id):
        return render_template('return_vehicle.html', booking_id=booking_id)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    from models.user import User
    if not User.query.filter_by(email='admin@carvax.com').first():
        admin = User(name='Administrator', email='admin@carvax.com', role='admin')
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
