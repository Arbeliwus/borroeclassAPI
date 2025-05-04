from flask import Blueprint, request, jsonify
from flask import Flask
from flask import Flask, request, jsonify
import pyodbc
from collections import OrderedDict
import json
from flask import Response
from datetime import datetime
from config import DB
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
calssdata_routes = Blueprint("calssdata_routes", __name__)

#顯示可借教室
@calssdata_routes.route('/api/remainclass')
def remain_class():
    try:
        name = request.args.get('name')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if not name or not start_time or not end_time:
            return jsonify({"message": "請提供完整的查詢參數"}), 400
        
        start_dt = datetime.strptime(start_time, "%Y-%m-%d")
        end_dt = datetime.strptime(end_time, "%Y-%m-%d")

        delta_days = (end_dt - start_dt).days

        one_month_days = 30

        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")

        if delta_days <= one_month_days:
            weekday_name = start_dt.strftime("%A")
            sql = f"SELECT {weekday_name} FROM NHU_CST.dbo.classrooms WHERE name = ? AND created_at IS NOT NULL"

        else:

            sql = f"SELECT * FROM NHU_CST.dbo.classrooms WHERE name = ? AND created_at IS NOT NULL"

        cursor.execute(sql, (name,))
        result = cursor.fetchall()
        result_dict = [dict(zip([column[0] for column in cursor.description], row)) for row in result]

        cursor.close()
        db.close()

        if result_dict:
            return jsonify({"result": result_dict}), 200
        else:
            return jsonify({"message": "未找到符合條件的資料"}), 404
        
    except Exception as e:
        # 若發生錯誤，返回詳細錯誤信息
        return jsonify({"message": f"借用查詢失敗，錯誤：{str(e)}"}), 500
        
#查詢教室借出狀態
@calssdata_routes.route('/api/classstatus')
def class_status():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"message": "請提供有效的 name 參數"}), 400
        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")
        sql = f"SELECT * FROM NHU_CST.dbo.classrooms WHERE name = ? AND created_at IS NOT NULL"
        cursor.execute(sql, (name,))
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]  # 獲取欄位名稱
            result = [dict(zip(columns, row)) for row in rows]  # 轉換成 list[dict]
        else:
            result = None

        cursor.close()
        db.close()
        if result:
            return jsonify({"result": result}), 200
        else:
            return jsonify({"message": "未找到符合條件的資料"}), 404
    except Exception as e:
        # 若發生錯誤，返回詳細錯誤信息
        return jsonify({"message": f"借用查詢失敗，錯誤：{str(e)}"}), 500
    
#查詢所有教室
@calssdata_routes.route('/api/allclass')
def all_class():
    conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

    db = pyodbc.connect(conn_str)
    cursor = db.cursor()
    print("資料庫連接成功")

    sql = f"SELECT name FROM [NHU_CST].[dbo].[classrooms] where created_at IS NOT NULL"

    cursor.execute(sql,)
    rows = cursor.fetchall()
    result = [{"name": row[0]} for row in rows] 
    cursor.close()
    db.close()


    return  result


#查詢教室與學生
@calssdata_routes.route('/api/class_sid')
def class_sid():
    try:
        cid = request.args.get('cid')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if not cid or not start_time or not end_time:
            return jsonify({"message": "請提供完整的查詢參數"}), 400
        
        start_dt = datetime.strptime(start_time, "%Y-%m-%d")
        end_dt = datetime.strptime(end_time, "%Y-%m-%d")

        conn_str = f"DRIVER={{SQL Server}};SERVER={DB['server']},{DB['port']};DATABASE={DB['database']};UID={DB['username']};PWD={DB['password']}"

        db = pyodbc.connect(conn_str)
        cursor = db.cursor()
        print("資料庫連接成功")


        sql = f"SELECT [sid],[start_date],[end_date]FROM [NHU_CST].[dbo].[borrow]WHERE  cid = ? AND start_date >= ? AND  end_date <= ? "

        cursor.execute(sql, (cid,start_dt, end_dt))  # 執行查詢
        result = cursor.fetchall()

        columns = [column[0] for column in cursor.description]  # 獲取列名
        data = []

        # 處理結果，將每一行轉換為有序字典
        for row in result:
            row_dict = dict(zip(columns, row))
            ordered_row = OrderedDict([
                ("sid", row_dict.get("sid")),
                ("start_date", row_dict.get("start_date")),
                ("end_date", row_dict.get("end_date"))
            ])
            data.append(ordered_row)
        
        cursor.close()
        db.close()

        # 返回結果
        if data:
            return Response(json.dumps(data, ensure_ascii=False, default=str), mimetype='application/json')
        else:
            return jsonify({"message": "未找到符合條件的資料"}), 404
        
    except Exception as e:
        # 若發生錯誤，返回詳細錯誤信息
        return jsonify({"message": f"借用查詢失敗，錯誤：{str(e)}"}), 500
