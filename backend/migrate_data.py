import os
import mysql.connector
from datetime import datetime
from run import create_app, db

# 导入所有需要迁移的数据库模型
from models.set_type import SetType
from models.stat_type import StatType
from models.drive_piece import DrivePiece, DrivePieceSubstat
from models.upgrade_record import UpgradeRecord

# ==================== 配置你的 MySQL 数据库连接信息 ====================
# 将 host 替换为你的 Ubuntu 服务器的公共 IP 地址
MYSQL_CONFIG = {
    'user': 'root',
    'password': '123456',
    'host': '117.72.163.11',  # <-- 这里是关键修改
    'database': 'zzz_drive_stats'
}
# ====================================================================

def migrate_data():
    """
    从 MySQL 数据库迁移数据到 SQLite 数据库。
    """
    app = create_app()

    with app.app_context():
        try:
            print("正在连接到远程 MySQL 数据库...")
            mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
            mysql_cursor = mysql_conn.cursor(dictionary=True)
            print("成功连接到远程 MySQL。")
            
            # 清空 SQLite 数据库中的所有相关表，以避免重复数据
            print("正在清空 SQLite 数据库...")
            db.session.query(UpgradeRecord).delete()
            db.session.query(DrivePieceSubstat).delete()
            db.session.query(DrivePiece).delete()
            db.session.query(StatType).delete()
            db.session.query(SetType).delete()
            db.session.commit()
            print("SQLite 数据库相关表已清空。")

            # === 1. 迁移 set_types 表 ===
            print("开始迁移 'set_types' 表...")
            mysql_cursor.execute("SELECT * FROM set_types")
            set_types_data = mysql_cursor.fetchall()
            db.session.bulk_insert_mappings(SetType, set_types_data)
            db.session.commit()
            print(f"成功迁移 {len(set_types_data)} 条套装数据。")

            # === 2. 迁移 stat_types 表 ===
            print("开始迁移 'stat_types' 表...")
            mysql_cursor.execute("SELECT * FROM stat_types")
            stat_types_data = mysql_cursor.fetchall()
            db.session.bulk_insert_mappings(StatType, stat_types_data)
            db.session.commit()
            print(f"成功迁移 {len(stat_types_data)} 条词条数据。")

            # === 3. 迁移 drive_pieces 表 ===
            print("开始迁移 'drive_pieces' 表...")
            mysql_cursor.execute("SELECT * FROM drive_pieces")
            drive_pieces_data = mysql_cursor.fetchall()
            db.session.bulk_insert_mappings(DrivePiece, drive_pieces_data)
            db.session.commit()
            print(f"成功迁移 {len(drive_pieces_data)} 条驱动盘数据。")
            
            # === 4. 迁移 drive_piece_substats 表 ===
            print("开始迁移 'drive_piece_substats' 表...")
            mysql_cursor.execute("SELECT * FROM drive_piece_substats")
            substats_data = mysql_cursor.fetchall()
            db.session.bulk_insert_mappings(DrivePieceSubstat, substats_data)
            db.session.commit()
            print(f"成功迁移 {len(substats_data)} 条副词条关联数据。")

            # === 5. 迁移 upgrade_records 表 ===
            print("开始迁移 'upgrade_records' 表...")
            mysql_cursor.execute("SELECT * FROM upgrade_records")
            upgrade_records_data = mysql_cursor.fetchall()
            db.session.bulk_insert_mappings(UpgradeRecord, upgrade_records_data)
            db.session.commit()
            print(f"成功迁移 {len(upgrade_records_data)} 条强化记录数据。")

            print("\n所有数据已成功迁移！")

        except mysql.connector.Error as e:
            print(f"MySQL 连接或查询错误: {e}")
            db.session.rollback()
        except Exception as e:
            print(f"迁移过程中发生错误: {e}")
            db.session.rollback()
        finally:
            if 'mysql_conn' in locals() and mysql_conn.is_connected():
                mysql_cursor.close()
                mysql_conn.close()
                print("MySQL 连接已关闭。")

if __name__ == '__main__':
    migrate_data()