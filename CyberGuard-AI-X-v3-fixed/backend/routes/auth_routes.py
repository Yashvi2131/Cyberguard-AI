"""
CyberGuard AI X - Authentication Routes
JWT-based login, registration, logout
"""

import bcrypt
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.db import execute_query

auth_bp = Blueprint('auth', __name__)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'user')

    if not all([name, email, password]):
        return jsonify({'error': 'Name, email and password are required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if role not in ['admin', 'user']:
        role = 'user'

    try:
        existing = execute_query(
            "SELECT id FROM users WHERE email = %s", (email,), fetchone=True
        )
        if existing:
            return jsonify({'error': 'Email already registered'}), 409

        hashed_pw = hash_password(password)
        user_id = execute_query(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_pw, role), commit=True
        )
        return jsonify({'message': 'Registration successful', 'user_id': user_id}), 201

    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    try:
        user = execute_query(
            "SELECT id, name, email, password, role FROM users WHERE email = %s",
            (email,), fetchone=True
        )
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    if not user or not check_password(password, user['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user['id']))

    ip_address = request.remote_addr or '0.0.0.0'
    try:
        execute_query(
            "INSERT INTO login_logs (user_id, ip_address) VALUES (%s, %s)",
            (user['id'], ip_address), commit=True
        )
    except Exception:
        pass  # Non-critical — don't fail login if log fails

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
    })


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = execute_query(
        "SELECT id, name, email, role, created_at FROM users WHERE id = %s",
        (user_id,), fetchone=True
    )
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user})


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Admin only: get all users"""
    user_id = int(get_jwt_identity())
    current_user = execute_query(
        "SELECT role FROM users WHERE id = %s", (user_id,), fetchone=True
    )
    if not current_user or current_user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    users = execute_query(
        "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC",
        fetchall=True
    )
    return jsonify({'users': users or []})


@auth_bp.route('/seed-admin', methods=['GET', 'POST'])
def seed_admin():
    """Create default admin if not exists (first-time setup only)"""
    existing = execute_query(
        "SELECT id FROM users WHERE role = 'admin' LIMIT 1", fetchone=True
    )
    if existing:
        return jsonify({'message': 'Admin already exists'}), 409

    hashed_pw = hash_password('Admin@123')
    user_id = execute_query(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        ('Admin', 'admin@cyberguard.ai', hashed_pw, 'admin'), commit=True
    )
    return jsonify({'message': 'Admin created', 'email': 'admin@cyberguard.ai', 'password': 'Admin@123'})
