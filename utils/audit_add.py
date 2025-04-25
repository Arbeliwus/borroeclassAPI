from flask import Blueprint
from utils.auth import token_required  # 驗證 Token 的裝飾器
#from models.database import review_request  # 假設有一個處理審核的函數
import config
from config import DB
import pyodbc
from flask import Flask
from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from config import DB
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

add_routes = Blueprint("add_routes", __name__)


#新增教室
@add_routes.route('/add_classroom', methods=['POST'])
@token_required
def add_classroom():
    data = request.get_json()

    if "name" not in data:
        return jsonify({"error": "請提供教室名稱"}), 400

    name = data["name"]
    week_data = {day: data.get(day, None) for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]}

    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"
        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")

        # 檢查是否有相同名稱且未被軟刪除的教室
        cursor.execute("SELECT id FROM NHU_CST.dbo.classrooms WHERE name = ? AND created_at IS NOT NULL", (name,))
        existing_classroom = cursor.fetchone()

        if existing_classroom:
            return jsonify({"error": "該教室名稱已存在，請使用其他名稱"}), 400

        # 檢查是否有相同名稱但已被軟刪除的教室
        cursor.execute("SELECT id FROM NHU_CST.dbo.classrooms WHERE name = ? AND created_at IS NULL", (name,))
        soft_deleted_classroom = cursor.fetchone()

        if soft_deleted_classroom:
            # 如果有，則恢復該教室
            cursor.execute("UPDATE NHU_CST.dbo.classrooms SET created_at = GETDATE() WHERE id = ?", (soft_deleted_classroom[0],))
        else:
            # 否則插入新的教室
            sql = """
            INSERT INTO NHU_CST.dbo.classrooms (name, monday, tuesday, wednesday, thursday, friday, saturday, sunday, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            values = [name] + list(week_data.values())
            cursor.execute(sql, values)

        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({"message": "教室新增成功"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

