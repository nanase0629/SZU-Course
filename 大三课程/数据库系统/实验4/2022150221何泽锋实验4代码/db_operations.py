import mysql.connector
from config import DB_CONFIG

def get_item_details(item_id):
    """获取物品详情"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 使用一个查询获取所有需要的信息
        query = """
        SELECT 
            p.*,
            u.用户姓名 as 发布人姓名,
            u.联系电话 as 发布人电话
        FROM 物品表 p
        LEFT JOIN 用户表 u ON p.发布人编号 = u.用户编号
        WHERE p.物品编号 = %s
        """
        
        cursor.execute(query, (item_id,))
        result = cursor.fetchone()
        cursor.close()  # 显式关闭游标
        
        return result
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def register_user(user_data):
    """注册新用户"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 先调用存储过程获取新用户ID
        cursor.execute("SET @new_id = NULL")
        cursor.execute("CALL 生成用户编号()")
        cursor.execute("SELECT @new_id")
        new_id = cursor.fetchone()[0]
        
        # 确保获取到了新ID
        if not new_id:
            raise Exception("无法生成新用户ID")
            
        # 插入新用户数据
        insert_query = """
        INSERT INTO 用户表 (
            用户编号, 用户姓名, 住址, 联系电话, 
            电子邮箱, 详细地址, 用户类型, 登录密码
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            new_id,
            user_data['用户姓名'],
            user_data.get('住址', ''),
            user_data.get('联系电话', ''),
            user_data.get('电子邮箱', ''),
            user_data.get('详细地址', ''),
            user_data.get('用户类型', '普通用户'),
            user_data['登录密码']
        )
        
        cursor.execute(insert_query, values)
        conn.commit()
        
        return new_id
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        if 'conn' in locals():
            conn.rollback()
        return None
    except Exception as e:
        print(f"错误: {e}")
        if 'conn' in locals():
            conn.rollback()
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

