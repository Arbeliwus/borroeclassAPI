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

delete_routes = Blueprint("delete_routes", __name__)



#刪除借用資料 #
@delete_routes.route('/delete_borrow', methods=['PUT'])
@token_required
def delete_borrow():
    id = request.args.get('id')

    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")
        sql = f"UPDATE [NHU_CST].[dbo].[borrow] SET created_at = NULL WHERE id =? ;"
        cursor.execute(sql, (id,))

        db.commit()
 
        cursor.close()
        db.close()
        return jsonify({"message": "刪除成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

#刪除教室
@delete_routes.route('/delete_class/', methods=['PUT'])
@token_required
def delete_class():
    id = request.args.get('id')

    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")
        sql = f"UPDATE [NHU_CST].[dbo].[classrooms] SET created_at = NULL WHERE id =? ;"
        cursor.execute(sql, (id,))

        db.commit()
 
        cursor.close()
        db.close()
        return jsonify({"message": "刪除成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500