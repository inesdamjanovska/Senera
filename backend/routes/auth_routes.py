from flask import request, jsonify, session, send_from_directory
from db.models import User, db
import re

def setup_auth_routes(app):
    
    @app.route('/register.html')
    def serve_register_html():
        return send_from_directory('../frontend', 'register.html')
    
    @app.route('/login.html')
    def serve_login_html():
        return send_from_directory('../frontend', 'login.html')
    
    @app.route('/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            
            # Validation
            display_name = data.get('display_name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            not_robot = data.get('not_robot', False)
            
            # Basic validation
            errors = []
            
            if not display_name or len(display_name) < 2:
                errors.append('Display name must be at least 2 characters long')
            
            if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                errors.append('Please enter a valid email address')
            
            if not password or len(password) < 6:
                errors.append('Password must be at least 6 characters long')
            
            if password != confirm_password:
                errors.append('Passwords do not match')
            
            if not not_robot:
                errors.append('Please confirm you are not a robot')
            
            if errors:
                return jsonify({'error': '; '.join(errors)}), 400
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': 'An account with this email already exists'}), 400
            
            # Create new user
            new_user = User(
                display_name=display_name,
                email=email
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the user
            session['user_id'] = new_user.id
            session['user_email'] = new_user.email
            session['user_name'] = new_user.display_name
            
            return jsonify({
                'message': 'Account created successfully!',
                'user': new_user.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    
    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Find user
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 401
            
            # Log in the user
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.display_name
            
            return jsonify({
                'message': 'Login successful!',
                'user': user.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Login failed: {str(e)}'}), 500
    
    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200
    
    @app.route('/current-user', methods=['GET'])
    def get_current_user():
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        return jsonify({'user': user.to_dict()}), 200

def require_login():
    """Helper function to check if user is logged in"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required. Please log in.'}), 401
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_active:
        session.clear()
        return jsonify({'error': 'Invalid session. Please log in again.'}), 401
    
    return None  # No error, user is authenticated

def get_current_user_id():
    """Helper function to get current user ID"""
    return session.get('user_id')