"""
个人资料统计API
获取博客文章数量、照片数量和工具数量
"""
from flask import Blueprint, jsonify
from models.blog import Post
from models.travel_photo import TravelPhoto
from database import db

profile_stats_bp = Blueprint('profile_stats', __name__, url_prefix='/api')

@profile_stats_bp.route('/profile/stats', methods=['GET'])
def get_profile_stats():
    """
    获取个人资料统计数据
    包括文章数量、照片数量和工具数量
    """
    try:
        # 获取博客文章总数
        posts_count = Post.query.count()
        
        # 获取旅行照片总数
        photos_count = TravelPhoto.query.count()
        
        # 工具数量（基于ToolboxPage中的静态数据）
        tools_count = 2  # 目前有：绝区零驱动器统计工具、海棠旅记
        
        return jsonify({
            'posts': posts_count,
            'photos': photos_count,
            'tools': tools_count
        })
        
    except Exception as e:
        return jsonify({
            'error': '获取统计数据失败',
            'details': str(e),
            'posts': 0,
            'photos': 0,
            'tools': 2  # 默认工具数量
        }), 500
