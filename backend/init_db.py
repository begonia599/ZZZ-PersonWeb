import os
from datetime import datetime

# 导入应用工厂和数据库实例
from run import create_app, db

# 导入所有需要创建的数据库模型
from models.set_type import SetType
from models.stat_type import StatType
from models.drive_piece import DrivePiece, DrivePieceSubstat
from models.upgrade_record import UpgradeRecord

def initialize_database():
    """
    初始化 drive_stats.db 数据库，创建所有表结构。
    不插入任何初始数据，用户可以自行导入数据。
    """
    # 创建一个 Flask 应用实例
    app = create_app()

    # 进入应用上下文，以便 SQLAlchemy 可以连接到数据库
    with app.app_context():
        try:
            # 确保实例文件夹存在
            os.makedirs(app.instance_path, exist_ok=True)
            
            print("正在删除旧的数据库表（如果存在）...")
            # 删除所有表（重新开始）
            db.drop_all(bind_key='drive_stats')
            
            print("正在创建新的数据库表...")
            # 创建所有数据库表
            db.create_all(bind_key='drive_stats')
            print("所有数据库表已创建。")
            
            # 检查表创建情况
            print("\n检查创建的表:")
            inspector = db.inspect(db.get_engine(bind='drive_stats'))
            tables = inspector.get_table_names()
            for table in tables:
                print(f"  ✅ {table}")
                
                # 显示每个表的列信息
                columns = inspector.get_columns(table)
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"    - {col['name']} ({col['type']}) {nullable}")
            
            print(f"\n数据库文件位置: {os.path.join(app.instance_path, 'drive_stats.db')}")
            print("数据库表结构创建完成，可以开始导入您的数据了。")
                
        except Exception as e:
            db.session.rollback()
            print(f"初始化数据库时发生错误: {e}")
            raise e

if __name__ == '__main__':
    initialize_database()