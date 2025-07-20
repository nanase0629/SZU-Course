import mysql.connector
from config import DB_CONFIG

def apply_for_claim(item_id, claimer_id):
    """申请认领物品"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 调用申请认领存储过程
        cursor.callproc('申请认领物品', (item_id, claimer_id))
        conn.commit()
        
        return True
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def process_claim(claim_id, new_status):
    """处理认领申请"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 调用处理认领申请存储过程
        cursor.callproc('处理认领申请', (claim_id, new_status))
        conn.commit()
        
        return True
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_claimable_items():
    """获取可认领的物品列表（拾获状态）"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM 物品表
            WHERE 物品状态 = '拾获'
            AND 物品编号 NOT IN (
                SELECT 物品编号 
                FROM 认领记录表 
                WHERE 认领状态 = '待处理' OR 认领状态 = '已通过'
            )
        """)
        
        return cursor.fetchall()
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
