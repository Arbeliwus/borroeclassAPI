from flask import Blueprint, request, jsonify
import bcrypt
from models.database import get_user
from utils.auth import generate_token

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    """驗證使用者帳號密碼，成功後發送 JWT"""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "請提供 username 和 password"}), 400

    username = data['username']
    password = data['password']

    stored_password_hash = get_user(username)
    if stored_password_hash and bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
        token = generate_token(username)
        return jsonify({"message": "登入成功", "token": token})
    
    return jsonify({"error": "帳號或密碼錯誤"}), 401
