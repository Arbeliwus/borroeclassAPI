from flask import Blueprint, jsonify, request
from utils.auth import token_required

protected_routes = Blueprint("protected_routes", __name__)

@protected_routes.route('/protected', methods=['GET'])
@token_required
def protected():
    """受保護的 API，需登入才能使用"""
    return jsonify({"message": f"Hello, {request.user['username']}! 你已成功登入。"})
