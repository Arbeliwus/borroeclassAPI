from flask import Blueprint, request, jsonify
from flask import Flask
from flask import Response
import json
from collections import OrderedDict
from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from config import DB
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

borrowdata_routes = Blueprint("borrowdata_routes", __name__)

# 顯示所有借用資料
@borrowdata_routes.route('/api/borrow_data')    
def borrow_data():
    conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"
    db = pyodbc.connect(conn_str)
    cursor = db.cursor()
    print("資料庫連接成功")
    sql = f"SELECT *FROM [NHU_CST].[dbo].[borrow] WHERE created_at IS NOT NULL" 
    cursor.execute(sql)
    result = cursor.fetchall()

    columns = [column[0] for column in cursor.description]
    
    classroom_cache = {}
     
     
    data = []
    for row in result:
        row_dict = dict(zip(columns, row))
        
        cid = row_dict.get("cid")

        # 如果 cache 裡面沒有，就查一次
        if cid not in classroom_cache:
            cursor.execute("SELECT name FROM [NHU_CST].[dbo].[classrooms] WHERE id = ?", cid)
            classroom_row = cursor.fetchone()
            classroom_name = classroom_row[0] if classroom_row else None
            classroom_cache[cid] = classroom_name
        else:
            classroom_name = classroom_cache[cid]
            
            
        ordered_row = OrderedDict([
            ("id", row_dict.get("id")),
            ("sid", row_dict.get("sid")),
            ("cid", classroom_name),
            ("departments", row_dict.get("departments")),
            ("borrow_numbers", row_dict.get("borrow_numbers")),
            ("borrow_reason", row_dict.get("borrow_reason")),
            ("borrow_weekdays", row_dict.get("borrow_weekdays")),
            ("start_date", row_dict.get("start_date")),
            ("end_date", row_dict.get("end_date")),
            ("borrow_section", row_dict.get("borrow_section")),
            ("created_at", row_dict.get("created_at")),
            ("is_approved", row_dict.get("is_approved")),
            ("approval_notes", row_dict.get("approval_notes")),
        ])
        data.append(ordered_row)

    cursor.close()
    db.close()

    data.reverse()

    return Response(json.dumps(data, ensure_ascii=False, default=str), mimetype='application/json')


