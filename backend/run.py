# backend/run.py
import os
import json
from flask import Flask, current_app
from database import db  # 从独立文件导入
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
import click
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # 确保使用正确的数据库路径
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(backend_dir, 'instance')
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev_secret_key',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(instance_dir, 'blog.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_BINDS={
            'blog_db': 'sqlite:///' + os.path.join(instance_dir, 'blog.db'),
            'drive_stats': 'sqlite:///' + os.path.join(instance_dir, 'drive_stats.db'),
            'travel_db': 'sqlite:///' + os.path.join(instance_dir, 'travel.db')
        }
    )

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={r"/api/*": {"origins": ["http://localhost", "http://localhost:5173"]}})

    app.logger.info("Firebase Admin SDK 未使用。指标将本地存储。")

    # 注册蓝图
    from blog_app.routes import blog_bp
    from metrics_app.routes import metrics_bp
    from drive_app.routes import drive_bp
    from travel_app.routes import travel_bp

    app.register_blueprint(blog_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(drive_bp)
    app.register_blueprint(travel_bp)

    # 注册CLI命令
    app.cli.add_command(init_metrics_command)
    app.cli.add_command(check_db_tables_command)

    # 自动初始化数据库表
    with app.app_context():
        try:
            # 创建所有数据库表
            db.create_all()
            app.logger.info("数据库表自动初始化完成")
            
            # 检查并记录创建的表
            from sqlalchemy import inspect
            
            # 检查主数据库
            inspector = inspect(db.engine)
            main_tables = inspector.get_table_names()
            app.logger.info(f"主数据库表: {main_tables}")
            
            # 检查驱动盘数据库
            if 'drive_stats' in db.engines:
                drive_inspector = inspect(db.get_engine(bind='drive_stats'))
                drive_tables = drive_inspector.get_table_names()
                app.logger.info(f"驱动盘数据库表: {drive_tables}")
                
        except Exception as e:
            app.logger.error(f"数据库初始化失败: {e}")

    # 注释掉自动创建表的代码，避免冲突
    # def create_tables():
    #     """创建所有数据库表"""
    #     try:
    #         # 导入所有模型以确保它们被注册
    #         from models.blog import Post
    #         from models.metrics import WebsiteMetrics
    #         from models.set_type import SetType
    #         from models.stat_type import StatType
    #         from models.drive_piece import DrivePiece, DrivePieceSubstat
    #         from models.upgrade_record import UpgradeRecord
            
    #         db.create_all()
    #         db.create_all(bind_key='blog_db')
    #         db.create_all(bind_key='drive_stats')
    #         app.logger.info("数据库表创建完成")
    #     except Exception as e:
    #         app.logger.error(f"创建数据库表时出错: {e}")

    # # 替代 before_first_request 的方法：在应用上下文中直接创建表
    # with app.app_context():
    #     create_tables()

    return app

@click.command('init-metrics')
def init_metrics_command():
    """初始化数据库中的网站指标。"""
    from models.metrics import WebsiteMetrics
    try:
        metrics_row = WebsiteMetrics.query.get(1)
        if not metrics_row:
            new_metrics = WebsiteMetrics(id=1, visitor_count=0, startup_time=datetime.utcnow())
            db.session.add(new_metrics)
            db.session.commit()
            current_app.logger.info("网站指标已在 SQLite 中初始化。")
        else:
            current_app.logger.info("网站指标已存在于 SQLite 中。")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"初始化 SQLite 中的网站指标时出错: {e}")

@click.command('check-db-tables')
@click.argument('db_name', default='all')
def check_db_tables_command(db_name):
    """检查数据库中是否存在预期的表。"""
    # 注释掉模型导入，避免启动时的冲突
    # from models.blog import Post
    # from models.metrics import WebsiteMetrics
    # from models.stat_type import StatType
    # from models.set_type import SetType
    # from models.drive_piece import DrivePiece, DrivePieceSubstat
    # from models.upgrade_record import UpgradeRecord

    expected_blog_tables = ['post', 'website_metrics']
    expected_drive_stats_tables = ['stat_types', 'set_types', 'drive_pieces', 'drive_piece_substats', 'upgrade_records']

    if db_name == 'all' or db_name == 'blog_db':
        print("\n--- 检查 blog.db ---")
        try:
            engine_blog = db.get_engine(bind='blog_db')
            inspector_blog = db.inspect(engine_blog)
            existing_blog_tables = inspector_blog.get_table_names()
            print(f"blog.db 中现有表: {existing_blog_tables}")
            for table in expected_blog_tables:
                if table in existing_blog_tables:
                    print(f"  ✅ 表 '{table}' 在 blog.db 中存在。")
                else:
                    print(f"  ❌ 表 '{table}' 在 blog.db 中缺失！")
        except Exception as e:
            print(f"  ❌ 无法连接或检查 blog.db: {e}")

    if db_name == 'all' or db_name == 'drive_stats':
        print("\n--- 检查 drive_stats.db ---")
        try:
            engine_drive = db.get_engine(bind='drive_stats')
            inspector_drive = db.inspect(engine_drive)
            existing_drive_tables = inspector_drive.get_table_names()
            print(f"drive_stats.db 中现有表: {existing_drive_tables}")
            for table in expected_drive_stats_tables:
                if table in existing_drive_tables:
                    print(f"  ✅ 表 '{table}' 在 drive_stats.db 中存在。")
                else:
                    print(f"  ❌ 表 '{table}' 在 drive_stats.db 中缺失！")
        except Exception as e:
            print(f"  ❌ 无法连接或检查 drive_stats.db: {e}")

app = create_app()

if __name__ == '__main__':
    # 直接运行python run.py时使用
    app.run(debug=True, port=5000)