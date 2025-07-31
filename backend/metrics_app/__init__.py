# backend/metrics_app/__init__.py
from flask import Blueprint

# 创建蓝图实例
metrics_bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')

# 导入路由，确保路由函数被注册到蓝图上
# 这行必须在 metrics_bp 定义之后
from . import routes