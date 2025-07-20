import mysql.connector
from config import DB_CONFIG
from datetime import datetime

def check_item_status(item_id):
    """检查物品状态是否可认领"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 物品状态
            FROM 物品认领视图
            WHERE 物品编号 = %s
        """, (item_id,))
        
        result = cursor.fetchone()
        if result:
            return result[0] != '丢失'
        return False
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def add_to_blacklist(user_id):
    """将用户加入失信名单"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 更新用户违规次数，触发器会自动处理失信名单
        cursor.execute("""
            UPDATE 用户表
            SET 违规次数 = 违规次数 + 1
            WHERE 用户编号 = %s
        """, (user_id,))
        
        conn.commit()
        return True
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def generate_new_user_id():
    """生成新用户ID"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SET @new_id = NULL")
        cursor.execute("CALL 生成用户编号()")
        cursor.execute("SELECT @new_id")
        result = cursor.fetchone()
        
        return result[0] if result else None
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        return None
    finally:
        cursor.close()
        conn.close()
