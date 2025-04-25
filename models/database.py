import pyodbc
import config

conn_str = f"DRIVER={{SQL Server}};SERVER={config.DB['server']},{config.DB['port']};DATABASE={config.DB['database']};UID={config.DB['username']};PWD={config.DB['password']}"

def get_db_connection():
    """建立資料庫連線"""
    return pyodbc.connect(conn_str)

def get_user(username):
    """從資料庫取得使用者密碼雜湊"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM admins WHERE name = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user[0] if user else None
    except Exception as e:
        return None

def test_connection():
    """測試資料庫連線"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        conn.close()
        return version[0]
    except Exception as e:
        return str(e)
def fetch_classrooms():
    """取得所有教室"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM classrooms")
        classrooms = [row.name for row in cursor.fetchall()]
        conn.close()
        return classrooms
    except Exception as e:
        return None
