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


#借用教室審核
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
    
#編輯借用資料
@review_routes.route('/edit_borrow/<int:id>', methods=['PUT'])
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
    

#刪除借用資料 #
@review_routes.route('/delete_borrow', methods=['PUT'])
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
    
#更改借用教室開放時間
@review_routes.route('/edit_class', methods=['PUT'])
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
    


@review_routes.route('/add_classroom', methods=['POST'])
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



#刪除教室 #
@review_routes.route('/delete_class', methods=['PUT'])
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