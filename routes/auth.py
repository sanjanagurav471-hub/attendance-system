from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db 
from models import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
from flask import render_template

@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template("register.html")

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        if not all(k in data for k in ['username', 'email', 'password', 'first_name', 'last_name']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'student')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    """Login user"""
    try:
        data = request.get_json() if request.is_json else request.form
        if request.method == 'GET':
            return render_template("login.html")
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'User account is disabled'}), 403
        
        login_user(user, remember=data.get('remember', False))
        
        return redirect(url_for('dashboard.dashboard_page'))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@auth_bp.route('/logout')
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    user = current_user
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'created_at': user.created_at.isoformat()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user = current_user
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            if User.query.filter_by(email=data['email']).first() and user.email != data['email']:
                return jsonify({'error': 'Email already exists'}), 409
            user.email = data['email']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500