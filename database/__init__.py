"""
初始化数据库
"""
from database.schema import DatabaseManager

def init_db():
    """初始化数据库，创建必要的表"""
    db_manager = DatabaseManager()
    db_manager.create_tables()
    print("数据库初始化完成")

if __name__ == "__main__":
    init_db()
