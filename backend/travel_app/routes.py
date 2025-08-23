import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from database import db
from models.travel_photo import TravelPhoto
from PIL import Image
import mimetypes

# 创建一个蓝图实例，所有与旅行相册相关的路由都将注册到这个蓝图上
travel_bp = Blueprint('travel', __name__, url_prefix='/api/travel')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 图片分类列表
VALID_CATEGORIES = {'风景', '人物', '美食', '建筑', '游戏截图', '生活记录', '其他'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_path():
    """获取上传文件夹路径"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(backend_dir, 'uploads', 'travel')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def get_thumbnail_path():
    """获取缩略图文件夹路径"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    thumbnail_dir = os.path.join(backend_dir, 'uploads', 'travel', 'thumbnails')
    os.makedirs(thumbnail_dir, exist_ok=True)
    return thumbnail_dir

def create_thumbnail(image_path, thumbnail_path, size=(300, 300)):
    """创建缩略图"""
    try:
        with Image.open(image_path) as img:
            # 保持宽高比的缩略图
            img.thumbnail(size, Image.Resampling.LANCZOS)
            # 如果是RGBA模式，转换为RGB
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            img.save(thumbnail_path, 'JPEG', quality=85)
            return True
    except Exception as e:
        current_app.logger.error(f"创建缩略图失败: {e}")
        return False

@travel_bp.route('/upload', methods=['POST'])
def upload_photo():
    """上传照片"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 获取表单数据
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        
        # 验证必填字段
        if not title:
            return jsonify({'error': '照片标题不能为空'}), 400
        
        if not category or category not in VALID_CATEGORIES:
            return jsonify({'error': '请选择有效的分类'}), 400
        
        # 检查文件大小（10MB限制）
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({'error': '文件大小不能超过10MB'}), 400
        
        # 生成唯一文件名
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        thumbnail_filename = f"thumb_{unique_filename.rsplit('.', 1)[0]}.jpg"
        
        # 保存原图
        upload_path = get_upload_path()
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # 创建缩略图
        thumbnail_path = get_thumbnail_path()
        thumbnail_file_path = os.path.join(thumbnail_path, thumbnail_filename)
        thumbnail_created = create_thumbnail(file_path, thumbnail_file_path)
        
        # 生成文件URL
        file_url = f"/api/travel/photos/file/{unique_filename}"
        thumbnail_url = f"/api/travel/photos/thumbnail/{thumbnail_filename}" if thumbnail_created else None
        
        # 获取MIME类型
        mime_type = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # 保存到数据库
        photo = TravelPhoto(
            title=title,
            description=description if description else None,
            category=category,
            file_name=unique_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=mime_type,
            url=file_url,
            thumbnail_url=thumbnail_url
        )
        
        db.session.add(photo)
        db.session.commit()
        
        current_app.logger.info(f"照片上传成功: {title} (ID: {photo.id})")
        
        return jsonify({
            'message': '照片上传成功',
            'photo': photo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"上传照片时出错: {e}")
        return jsonify({'error': '上传失败，请稍后重试'}), 500

@travel_bp.route('/photos', methods=['GET'])
def get_photos():
    """获取照片列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', '')
        sort_by = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')
        search = request.args.get('search', '')
        limit = request.args.get('limit', type=int)
        
        # 构建查询
        query = TravelPhoto.query
        
        # 分类筛选
        if category and category in VALID_CATEGORIES:
            query = query.filter(TravelPhoto.category == category)
        
        # 搜索筛选
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    TravelPhoto.title.like(search_term),
                    TravelPhoto.description.like(search_term)
                )
            )
        
        # 排序
        if sort_by == 'title':
            order_by = TravelPhoto.title.asc() if order == 'asc' else TravelPhoto.title.desc()
        else:  # 默认按创建时间排序
            order_by = TravelPhoto.created_at.asc() if order == 'asc' else TravelPhoto.created_at.desc()
        
        query = query.order_by(order_by)
        
        # 如果有limit参数，直接返回前N个结果
        if limit:
            photos = query.limit(limit).all()
            return jsonify([photo.to_dict() for photo in photos])
        
        # 分页
        per_page = min(per_page, 100)  # 限制最大每页数量
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'photos': [photo.to_dict() for photo in pagination.items],
            'pagination': {
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'total_items': pagination.total,
                'total_pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取照片列表时出错: {e}")
        return jsonify({'error': '获取照片列表失败'}), 500

@travel_bp.route('/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    """获取单张照片信息"""
    try:
        photo = TravelPhoto.query.get_or_404(photo_id)
        return jsonify(photo.to_dict())
    except Exception as e:
        current_app.logger.error(f"获取照片信息时出错: {e}")
        return jsonify({'error': '照片不存在'}), 404

@travel_bp.route('/photos/<int:photo_id>', methods=['PUT'])
def update_photo(photo_id):
    """更新照片信息"""
    try:
        photo = TravelPhoto.query.get_or_404(photo_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的JSON数据'}), 400
        
        # 更新字段
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({'error': '照片标题不能为空'}), 400
            photo.title = title
        
        if 'category' in data:
            category = data['category'].strip()
            if category and category not in VALID_CATEGORIES:
                return jsonify({'error': '请选择有效的分类'}), 400
            photo.category = category
        
        if 'description' in data:
            photo.description = data['description'].strip() if data['description'] else None
        
        db.session.commit()
        
        current_app.logger.info(f"照片信息更新成功: {photo.title} (ID: {photo.id})")
        return jsonify(photo.to_dict())
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新照片信息时出错: {e}")
        return jsonify({'error': '更新失败'}), 500

@travel_bp.route('/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    """删除照片"""
    try:
        photo = TravelPhoto.query.get_or_404(photo_id)
        
        # 删除文件
        try:
            if os.path.exists(photo.file_path):
                os.remove(photo.file_path)
            
            # 删除缩略图
            if photo.thumbnail_url:
                thumbnail_filename = photo.thumbnail_url.split('/')[-1]
                thumbnail_path = get_thumbnail_path()
                thumbnail_file_path = os.path.join(thumbnail_path, thumbnail_filename)
                if os.path.exists(thumbnail_file_path):
                    os.remove(thumbnail_file_path)
        except Exception as e:
            current_app.logger.warning(f"删除文件时出错: {e}")
        
        # 从数据库删除
        db.session.delete(photo)
        db.session.commit()
        
        current_app.logger.info(f"照片删除成功: {photo.title} (ID: {photo.id})")
        return jsonify({'message': '照片删除成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除照片时出错: {e}")
        return jsonify({'error': '删除失败'}), 500

@travel_bp.route('/photos/file/<filename>')
def get_photo_file(filename):
    """获取原图文件"""
    try:
        upload_path = get_upload_path()
        return send_from_directory(upload_path, filename)
    except Exception as e:
        current_app.logger.error(f"获取图片文件时出错: {e}")
        return jsonify({'error': '文件不存在'}), 404

@travel_bp.route('/photos/thumbnail/<filename>')
def get_thumbnail_file(filename):
    """获取缩略图文件"""
    try:
        thumbnail_path = get_thumbnail_path()
        return send_from_directory(thumbnail_path, filename)
    except Exception as e:
        current_app.logger.error(f"获取缩略图文件时出错: {e}")
        return jsonify({'error': '文件不存在'}), 404

@travel_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    return jsonify(list(VALID_CATEGORIES))

@travel_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    try:
        total_photos = TravelPhoto.query.count()
        
        # 按分类统计
        category_stats = db.session.query(
            TravelPhoto.category,
            db.func.count(TravelPhoto.id).label('count')
        ).group_by(TravelPhoto.category).all()
        
        # 按月份统计
        monthly_stats = db.session.query(
            db.func.strftime('%Y-%m', TravelPhoto.created_at).label('month'),
            db.func.count(TravelPhoto.id).label('count')
        ).group_by('month').order_by('month').all()
        
        return jsonify({
            'total_photos': total_photos,
            'category_stats': [{'category': cat, 'count': count} for cat, count in category_stats],
            'monthly_stats': [{'month': month, 'count': count} for month, count in monthly_stats]
        })
        
    except Exception as e:
        current_app.logger.error(f"获取统计信息时出错: {e}")
        return jsonify({'error': '获取统计信息失败'}), 500

