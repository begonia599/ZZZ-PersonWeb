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
    初始化 drive_stats.db 数据库，创建所有表并插入初始套装和词条数据。
    """
    # 创建一个 Flask 应用实例
    app = create_app()

    # 进入应用上下文，以便 SQLAlchemy 可以连接到数据库
    with app.app_context():
        try:
            # 确保实例文件夹存在
            os.makedirs(app.instance_path, exist_ok=True)
            
            # 创建所有数据库表
            db.create_all()
            print("所有数据库表已创建。")

            # 检查 set_types 表是否为空，避免重复插入
            if SetType.query.count() == 0:
                print("正在插入初始套装和词条数据...")
                
                initial_set_types = [
                    {'set_name': '空洞驰行', 'two_piece_effect': '攻击力+10%', 'four_piece_effect': '攻击力+20%'},
                    {'set_name': '电镀音潮', 'two_piece_effect': '雷属性伤害+10%', 'four_piece_effect': '雷属性伤害+20%'},
                    {'set_name': '虚数织构', 'two_piece_effect': '生命值+10%'},
                    {'set_name': '物理穿透', 'two_piece_effect': '物理伤害+10%'}
                ]
                initial_stat_types = [
                    {'stat_name': '暴击率'},
                    {'stat_name': '暴击伤害'},
                    {'stat_name': '攻击力百分比'},
                    {'stat_name': '攻击力'},
                    {'stat_name': '生命值百分比'},
                    {'stat_name': '生命值'},
                    {'stat_name': '防御力百分比'},
                    {'stat_name': '防御力'},
                    {'stat_name': '效果命中'},
                    {'stat_name': '效果抵抗'},
                    {'stat_name': '能量恢复效率'},
                    {'stat_name': '击破特攻'},
                    {'stat_name': '火属性伤害'},
                    {'stat_name': '冰属性伤害'},
                    {'stat_name': '雷属性伤害'},
                    {'stat_name': '风属性伤害'},
                    {'stat_name': '物理伤害'},
                    {'stat_name': '虚数伤害'},
                    {'stat_name': '量子伤害'}
                ]
                
                db.session.bulk_insert_mappings(SetType, initial_set_types)
                db.session.bulk_insert_mappings(StatType, initial_stat_types)
                db.session.commit()
                print("初始套装和词条数据已成功插入到 drive_stats.db。")
            else:
                print("drive_stats.db 中的套装和词条数据已存在，跳过初始化。")

        except Exception as e:
            db.session.rollback()
            print(f"初始化数据库时发生错误: {e}")
            
if __name__ == '__main__':
    initialize_database()