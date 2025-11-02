import os
import mysql.connector
from datetime import datetime, timedelta, timezone
from run import create_app, db

# 北京时区（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))

def get_beijing_now():
    """获取北京时间的当前时间"""
    return datetime.now(BEIJING_TZ)

# 导入所有需要迁移的数据库模型
from models.set_type import SetType
from models.stat_type import StatType
from models.drive_piece import DrivePiece, DrivePieceSubstat
from models.upgrade_record import UpgradeRecord

# MySQL 数据库连接信息
MYSQL_CONFIG = {
    'user': 'root',
    'password': '123456',
    'host': '117.72.163.11',
    'database': 'zzz_drive_stats'
}

def migrate_complete_data():
    """
    完整迁移 MySQL 数据到 SQLite，正确映射字段。
    """
    app = create_app()

    with app.app_context():
        try:
            print("🚀 开始完整数据迁移...")
            print("正在连接到远程 MySQL 数据库...")
            mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
            mysql_cursor = mysql_conn.cursor(dictionary=True)
            print("✅ 成功连接到远程 MySQL。")
            
            # 首先清空现有数据（完全重建）
            print("\n🗑️  清空现有数据...")
            db.session.query(UpgradeRecord).delete()
            db.session.query(DrivePieceSubstat).delete()
            db.session.query(DrivePiece).delete()
            db.session.query(StatType).delete()
            db.session.query(SetType).delete()
            db.session.commit()
            print("✅ 现有数据已清空。")

            # === 1. 迁移 set_types 表 ===
            print("\n📦 迁移套装类型数据...")
            mysql_cursor.execute("SELECT * FROM set_types ORDER BY set_id")
            mysql_set_types = mysql_cursor.fetchall()
            
            for mysql_record in mysql_set_types:
                # MySQL -> SQLite 字段映射（字段名一致）
                sqlite_record = SetType(
                    set_id=mysql_record['set_id'],  
                    set_name=mysql_record['set_name'],  
                    two_piece_effect=mysql_record.get('two_piece_effect'),
                    four_piece_effect=mysql_record.get('four_piece_effect')
                )
                db.session.add(sqlite_record)
                print(f"  ✓ 套装: {mysql_record['set_name']}")
            
            db.session.commit()
            print(f"✅ 完成套装类型迁移，共 {len(mysql_set_types)} 条记录。")

            # === 2. 迁移 stat_types 表 ===
            print("\n📊 迁移词条类型数据...")
            mysql_cursor.execute("SELECT * FROM stat_types ORDER BY stat_type_id")
            mysql_stat_types = mysql_cursor.fetchall()
            
            for mysql_record in mysql_stat_types:
                # MySQL -> SQLite 字段映射（字段名一致）
                sqlite_record = StatType(
                    stat_type_id=mysql_record['stat_type_id'],  
                    stat_name=mysql_record['stat_name'],  
                    stat_type='both'  # MySQL中没有这个字段，使用默认值
                )
                db.session.add(sqlite_record)
                print(f"  ✓ 词条: {mysql_record['stat_name']}")
            
            db.session.commit()
            print(f"✅ 完成词条类型迁移，共 {len(mysql_stat_types)} 条记录。")

            # === 3. 迁移 drive_pieces 表 ===
            print("\n🛡️  迁移驱动盘数据...")
            mysql_cursor.execute("SELECT * FROM drive_pieces ORDER BY drive_id")
            mysql_drive_pieces = mysql_cursor.fetchall()
            
            for mysql_record in mysql_drive_pieces:
                # MySQL -> SQLite 字段映射
                sqlite_record = DrivePiece(
                    drive_id=mysql_record['drive_id'],  # 字段名相同
                    set_id=mysql_record['set_id'],      # 字段名相同
                    position=mysql_record['position'],  # 字段名相同
                    main_stat_id=mysql_record['main_stat_id'],  # 字段名相同
                    main_stat_level=15,  # 默认值，MySQL中可能没有这个字段
                    total_upgrades=0,    # 默认值，MySQL中可能没有这个字段
                    substats=None,       # JSON字段，稍后通过关联表填充
                    created_at=mysql_record.get('created_at'),
                    updated_at=mysql_record.get('created_at')  # 使用created_at作为updated_at
                )
                db.session.add(sqlite_record)
                if mysql_record['drive_id'] % 100 == 0:  # 每100条显示一次进度
                    print(f"  ✓ 已处理 {mysql_record['drive_id']} 个驱动盘...")
            
            db.session.commit()
            print(f"✅ 完成驱动盘迁移，共 {len(mysql_drive_pieces)} 条记录。")
            
            # === 4. 迁移 drive_piece_substats 表 ===
            print("\n🔗 迁移副词条关联数据...")
            mysql_cursor.execute("SELECT * FROM drive_piece_substats ORDER BY id")
            mysql_substats = mysql_cursor.fetchall()
            
            for mysql_record in mysql_substats:
                # MySQL -> SQLite 字段映射（字段名一致）
                sqlite_record = DrivePieceSubstat(
                    drive_id=mysql_record['drive_id'],  # 字段名一致
                    stat_id=mysql_record['stat_id'],    # 字段名一致
                    created_at=mysql_record.get('created_at')
                )
                db.session.add(sqlite_record)
                if mysql_record['id'] % 500 == 0:  # 每500条显示一次进度
                    print(f"  ✓ 已处理 {mysql_record['id']} 个副词条关联...")
            
            db.session.commit()
            print(f"✅ 完成副词条关联迁移，共 {len(mysql_substats)} 条记录。")

            # === 5. 迁移 upgrade_records 表 ===
            print("\n⚡ 迁移强化记录数据...")
            mysql_cursor.execute("SELECT * FROM upgrade_records ORDER BY upgrade_id")
            mysql_upgrades = mysql_cursor.fetchall()
            
            for mysql_record in mysql_upgrades:
                # MySQL -> SQLite 字段映射（字段名一致）
                sqlite_record = UpgradeRecord(
                    upgrade_id=mysql_record['upgrade_id'],
                    drive_id=mysql_record['drive_id'],
                    substat_id=mysql_record['substat_id'],
                    is_original=bool(mysql_record['is_original']),  # tinyint -> boolean
                    upgrade_count=mysql_record['upgrade_count'],
                    created_at=mysql_record.get('created_at'),
                    updated_at=mysql_record.get('created_at')  # 使用created_at作为updated_at
                )
                db.session.add(sqlite_record)
                print(f"  ✓ 强化记录 ID: {mysql_record['upgrade_id']}")
            
            db.session.commit()
            print(f"✅ 完成强化记录迁移，共 {len(mysql_upgrades)} 条记录。")

            # === 数据迁移统计 ===
            print("\n📈 迁移完成统计:")
            print(f"  📦 套装类型: {len(mysql_set_types)} 条")
            print(f"  📊 词条类型: {len(mysql_stat_types)} 条")
            print(f"  🛡️  驱动盘: {len(mysql_drive_pieces)} 条")
            print(f"  🔗 副词条关联: {len(mysql_substats)} 条")
            print(f"  ⚡ 强化记录: {len(mysql_upgrades)} 条")
            print(f"  📊 总计: {len(mysql_set_types) + len(mysql_stat_types) + len(mysql_drive_pieces) + len(mysql_substats) + len(mysql_upgrades)} 条记录")

            print("\n🎉 数据迁移完成！")

        except mysql.connector.Error as e:
            print(f"❌ MySQL 连接或查询错误: {e}")
            db.session.rollback()
        except Exception as e:
            print(f"❌ 迁移过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
        finally:
            if 'mysql_conn' in locals() and mysql_conn.is_connected():
                mysql_cursor.close()
                mysql_conn.close()
                print("🔌 MySQL 连接已关闭。")

def backup_sqlite_before_migration():
    """
    迁移前备份SQLite数据库
    """
    import shutil
    
    timestamp = get_beijing_now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"instance/backup_before_migration_{timestamp}.db"
    
    try:
        if os.path.exists("instance/drive_stats.db"):
            shutil.copy2("instance/drive_stats.db", backup_file)
            print(f"💾 SQLite数据库已备份到: {backup_file}")
            return backup_file
        else:
            print("⚠️  没有找到现有的SQLite数据库文件")
            return None
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

if __name__ == '__main__':
    print("🌟 开始完整数据迁移流程...")
    
    # 备份现有数据
    backup_file = backup_sqlite_before_migration()
    if backup_file:
        print(f"📁 数据已备份，如需恢复可使用: {backup_file}")
    
    # 询问确认
    print("\n⚠️  警告: 此操作将完全替换现有的SQLite数据库内容！")
    print("请确保已经备份了重要数据。")
    
    # 在脚本中直接执行，不需要用户确认
    print("🚀 开始迁移...")
    migrate_complete_data()
