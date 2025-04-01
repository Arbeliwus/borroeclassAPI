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

review_routes = Blueprint("review_routes", __name__)

@review_routes.route('/review', methods=['POST'])
@token_required
def review():

    data = request.get_json()
    if not data or 'id' not in data or 'is_approved' not in data:
        return jsonify({"error": "請提供 id 和 is_approved"}), 400
    
    id = data['id']
    is_approved = data['is_approved']
    approval_notes = data.get('approval_notes', '')

    
    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")
        sql = f"UPDATE [NHU_CST].[dbo].[borrow] SET is_approved = ?, approval_notes = ? WHERE id = ?;"
        cursor.execute(sql, (is_approved,approval_notes,id))
        
 
        cursor.close()
        db.close()
        return jsonify({"message": "審核成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500