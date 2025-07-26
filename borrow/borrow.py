import json
from flask import Blueprint, request, jsonify
from flask import Flask
from routes.login import auth_routes
from routes.db_test import db_routes
from routes.JWT_API import protected_routes
from utils.audit import review_routes
from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from config import DB
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

borrow_routes = Blueprint("borrow_routes", __name__)

# 註冊藍圖（Blueprint）
app.register_blueprint(auth_routes)
app.register_blueprint(db_routes)
app.register_blueprint(protected_routes)
app.register_blueprint(review_routes)

#申請借用教室
@borrow_routes.route('/api/borrow', methods=['POST'])
def borrow_classroom():
    try:
        data = request.get_json()
        print("收到的 JSON:", data)

        sid = data.get('sid', None) #學號
        cid = data.get('cid', None) #教室編號
        departments = data.get('departments', None) #科系
        borrow_numbers = data.get('borrow_numbers', None) #借用人數
        borrow_reason = data.get('borrow_reason', None) #借用節數
        start_date = data.get('start_date', None) #開始時間
        end_date = data.get('end_date', None) #結束時間
        borrow_section = data.get('borrow_section', None) #使用說明
        weekdays = data.get('weekdays', [])  # 新增：借用星期幾，預設空陣列


        if not all([sid, cid, departments, borrow_numbers, borrow_reason, start_date,end_date,borrow_section]):
            return jsonify({"message": "借用失敗，每個項目皆為必填"}), 400
        
        weekdays_json = json.dumps(weekdays, ensure_ascii=False) 
        
        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"
        
        

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")
        sql = """
            INSERT INTO NHU_CST.dbo.borrow (
                sid, cid, departments, borrow_numbers, borrow_reason, 
                start_date, end_date, borrow_section, borrow_weekdays, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
         # 根據教室名稱查找 id
        cursor.execute("SELECT id FROM NHU_CST.dbo.classrooms WHERE name = ?", (cid,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"message": f"教室名稱 '{cid}' 無對應資料"}), 404

        cid = result[0]  # 拿到對應的 cid
        
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        values = (sid, cid, departments, borrow_numbers, borrow_reason, start_date, end_date, borrow_section, weekdays_json, created_at)
        cursor.execute(sql, values)
        db.commit()
        cursor.close()

        return jsonify({"message": "借用成功"}), 201
    except Exception as e:
        return jsonify({"message": f"借用失敗，錯誤：{str(e)}"}), 500