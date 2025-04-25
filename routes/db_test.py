from flask import Blueprint, jsonify
from models.database import test_connection,fetch_classrooms

db_routes = Blueprint("db_routes", __name__)

@db_routes.route('/db-T')
def test_db():
    """測試資料庫連線"""
    db_version = test_connection()
    return jsonify({"db_version": db_version})

@db_routes.route('/getClassrooms')
def getClassrooms():
    """取得所有教室"""
    classrooms = fetch_classrooms()
    return jsonify({"classrooms": classrooms})