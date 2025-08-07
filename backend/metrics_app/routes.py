from flask import Blueprint, jsonify, current_app, request
from datetime import datetime
import time

# 修改：从独立的 database 文件导入 db
from database import db  # 改为从 database.py 导入
from models.metrics import WebsiteMetrics

metrics_bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')

@metrics_bp.route('/visitor_count', methods=['GET'])
def get_visitor_count():
    """
    获取当前的网站访问人数。
    """
    try:
        metrics_row = WebsiteMetrics.query.get(1)
        if metrics_row:
            count = metrics_row.visitor_count
            current_app.logger.info(f"Retrieved visitor count from SQLite: {count}")
            return jsonify({"visitor_count": count})
        else:
            current_app.logger.warning("Website metrics row not found in SQLite. Initializing count to 0.")
            # 如果不存在，尝试初始化它 (这应该在 app 初始化时完成，这里作为兜底)
            new_metrics = WebsiteMetrics(id=1, visitor_count=0, startup_time=datetime.utcnow())
            db.session.add(new_metrics)
            db.session.commit() # 提交以确保记录存在
            return jsonify({"visitor_count": 0})
    except Exception as e:
        db.session.rollback() # 确保在异常发生时回滚会话
        current_app.logger.error(f"Error getting visitor count from SQLite: {e}")
        return jsonify({"error": "Failed to retrieve visitor count", "details": str(e)}), 500

@metrics_bp.route('/increment_visitor_count', methods=['POST'])
def increment_visitor_count():
    """
    增加网站访问人数。
    """
    try:
        metrics_row = WebsiteMetrics.query.get(1)
        if not metrics_row:
            # 如果不存在，初始化它并设置计数为 1
            new_metrics = WebsiteMetrics(id=1, visitor_count=1, startup_time=datetime.utcnow())
            db.session.add(new_metrics)
            db.session.commit()
            current_app.logger.info("Website metrics row created and visitor count initialized to 1 in SQLite.")
            return jsonify({"message": "Visitor count incremented", "new_count": 1})
        else:
            metrics_row.visitor_count += 1
            metrics_row.last_updated = datetime.utcnow() # 更新最后更新时间
            db.session.commit()
            current_app.logger.info(f"Visitor count incremented to: {metrics_row.visitor_count} in SQLite.")
            return jsonify({"message": "Visitor count incremented", "new_count": metrics_row.visitor_count})
    except Exception as e:
        db.session.rollback() # 确保在异常发生时回滚会话
        current_app.logger.error(f"Error incrementing visitor count in SQLite: {e}")
        return jsonify({"error": "Failed to increment visitor count", "details": str(e)}), 500

@metrics_bp.route('/uptime', methods=['GET'])
def get_website_uptime():
    """
    获取网站的启动时间戳。
    """
    try:
        metrics_row = WebsiteMetrics.query.get(1)
        if metrics_row and metrics_row.startup_time:
            startup_time_utc = metrics_row.startup_time
            # 计算运行时间（秒）
            uptime_seconds = (datetime.utcnow() - startup_time_utc).total_seconds()
            return jsonify({"startupTime": startup_time_utc.isoformat(), "uptimeSeconds": uptime_seconds}), 200
        else:
            current_app.logger.warning("Website metrics row or startup time not found in SQLite. Initializing.")
            # 如果不存在，尝试初始化它 (作为兜底)
            new_metrics = WebsiteMetrics(id=1, visitor_count=0, startup_time=datetime.utcnow())
            db.session.add(new_metrics)
            db.session.commit()
            # 再次尝试获取，或者直接返回初始化后的数据
            startup_timestamp_ms = int(new_metrics.startup_time.timestamp() * 1000)
            return jsonify({"startup_time_ms": startup_timestamp_ms}), 200 # 返回 200 而不是 500
    except Exception as e:
        db.session.rollback() # 确保在异常发生时回滚会话
        current_app.logger.error(f"Error getting website uptime from SQLite: {e}")
        return jsonify({"error": "Failed to retrieve website uptime", "details": str(e)}), 500