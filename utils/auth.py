import jwt
import datetime
from flask import request, jsonify
from functools import wraps
import config

def generate_token(username):
    """產生 JWT Token"""
    token_payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(token_payload, config.SECRET_KEY, algorithm="HS256")

def token_required(f):
    """JWT 驗證裝飾器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "未提供 Token"}), 403
        
        try:
            decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
            request.user = decoded_token
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token 已過期"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "無效的 Token"}), 403

        return f(*args, **kwargs)
    return decorated
