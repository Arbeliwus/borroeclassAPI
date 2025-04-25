from flask import Blueprint, request, jsonify
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

edit_routes = Blueprint("edit_routes", __name__)

#編輯借用資料
@edit_routes.route('/edit_borrow', methods=['PUT'])
@token_required
def edit_borrow():
    data = request.get_json()

    if "id" not in data:
        return jsonify({"error": "請提供 id"}), 400
    
    id = data.pop("id")  #取出修改編號

    if not data:
        return jsonify({"error": "沒有提供任何要更新的欄位"}), 400
    
    update_fields = []
    values = []
    for key, value in data.items():
        update_fields.append(f"{key} = ?")
        values.append(value)

    values.append(id)

    sql = f"""
    UPDATE [NHU_CST].[dbo].[borrow]
    SET {', '.join(update_fields)}
    WHERE id = ?;
    """

    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")
        cursor.execute(sql, tuple(values))
        db.commit()
 
        cursor.close()
        db.close()
        return jsonify({"message": "更新成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


    
#更改借用教室開放時間
@edit_routes.route('/edit_class', methods=['PUT'])
@token_required
def edit_class():
    data = request.get_json()

    if "id" not in data:
        return jsonify({"error": "請提供 id"}), 400
    
    id = data.pop("id")  #取出修改編號

    if not data:
        return jsonify({"error": "沒有提供任何要更新的欄位"}), 400
    
    update_fields = []
    values = []
    for key, value in data.items():
        update_fields.append(f"{key} = ?")
        values.append(value)

    values.append(id)

    sql = f"""
    UPDATE [NHU_CST].[dbo].[classrooms]
    SET {', '.join(update_fields)}
    WHERE id = ?;
    """

    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")
        cursor.execute(sql, tuple(values))
        db.commit()
 
        cursor.close()
        db.close()
        return jsonify({"message": "更新成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500