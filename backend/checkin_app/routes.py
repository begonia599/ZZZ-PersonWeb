import os
import uuid
from datetime import datetime, date, timedelta, timezone
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from database import db
from models.checkin import CheckinTask, CheckinRecord

# 北京时区（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))

def get_beijing_date():
    """获取北京时间的当前日期"""
    return datetime.now(BEIJING_TZ).date()

# 创建蓝图
checkin_bp = Blueprint('checkin', __name__, url_prefix='/api/checkin')

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_path():
    """获取上传文件夹路径"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(backend_dir, 'uploads', 'checkin')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def calculate_total_count(start_date, end_date, frequency, custom_days=None):
    """计算总打卡次数"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    delta = (end_date - start_date).days + 1  # 包含结束日期
    
    if frequency == 'daily':
        return delta
    elif frequency == 'weekly':
        return delta // 7
    elif frequency == 'monthly':
        return delta // 30
    elif frequency == 'custom' and custom_days:
        return delta // custom_days
    else:
        return delta

@checkin_bp.route('/tasks', methods=['POST'])
def create_task():
    """创建打卡任务"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的JSON数据'}), 400
        
        # 验证必填字段
        title = data.get('title', '').strip()
        if not title:
            return jsonify({'error': '任务名称不能为空'}), 400
        
        frequency = data.get('frequency', '').strip()
        if frequency not in ['daily', 'weekly', 'monthly', 'custom']:
            return jsonify({'error': '无效的打卡频率'}), 400
        
        custom_days = data.get('custom_days')
        if frequency == 'custom' and not custom_days:
            return jsonify({'error': '自定义频率需要指定天数'}), 400
        
        # 日期处理
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        
        if end_date < start_date:
            return jsonify({'error': '结束日期不能早于开始日期'}), 400
        
        # 是否长期任务
        is_long_term = data.get('is_long_term', False)
        duration = data.get('duration')
        
        # 计算总打卡次数
        total_count = calculate_total_count(start_date, end_date, frequency, custom_days)
        
        # 创建任务
        task = CheckinTask(
            title=title,
            frequency=frequency,
            custom_days=custom_days,
            start_date=start_date,
            end_date=end_date,
            total_count=total_count,
            checked_count=0,
            is_long_term=is_long_term,
            is_terminated=False,
            duration=duration
        )
        
        db.session.add(task)
        db.session.commit()
        
        current_app.logger.info(f"打卡任务创建成功: {title} (ID: {task.id})")
        
        return jsonify({
            'message': '任务创建成功',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建打卡任务时出错: {e}")
        return jsonify({'error': f'创建失败: {str(e)}'}), 500

@checkin_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """获取所有打卡任务"""
    try:
        tasks = CheckinTask.query.order_by(CheckinTask.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
        
    except Exception as e:
        current_app.logger.error(f"获取打卡任务列表时出错: {e}")
        return jsonify({'error': '获取任务列表失败'}), 500

@checkin_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """获取单个打卡任务"""
    try:
        task = CheckinTask.query.get_or_404(task_id)
        return jsonify(task.to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取打卡任务时出错: {e}")
        return jsonify({'error': '任务不存在'}), 404

@checkin_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除打卡任务"""
    try:
        task = CheckinTask.query.get_or_404(task_id)
        
        # 删除相关的打卡记录图片
        for record in task.records:
            if record.image_path and os.path.exists(record.image_path):
                try:
                    os.remove(record.image_path)
                except Exception as e:
                    current_app.logger.warning(f"删除图片文件失败: {e}")
        
        db.session.delete(task)
        db.session.commit()
        
        current_app.logger.info(f"打卡任务删除成功: {task.title} (ID: {task.id})")
        return jsonify({'message': '任务删除成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除打卡任务时出错: {e}")
        return jsonify({'error': '删除失败'}), 500

@checkin_bp.route('/tasks/<int:task_id>/terminate', methods=['POST'])
def terminate_task(task_id):
    """终止长期任务"""
    try:
        task = CheckinTask.query.get_or_404(task_id)
        
        if not task.is_long_term:
            return jsonify({'error': '只有长期任务可以被终止'}), 400
        
        if task.is_terminated:
            return jsonify({'error': '任务已经被终止'}), 400
        
        task.is_terminated = True
        task.end_date = get_beijing_date()
        
        db.session.commit()
        
        current_app.logger.info(f"长期任务终止成功: {task.title} (ID: {task.id})")
        return jsonify({
            'message': '任务已终止',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"终止任务时出错: {e}")
        return jsonify({'error': '终止失败'}), 500

@checkin_bp.route('/records', methods=['POST'])
def create_record():
    """创建打卡记录"""
    try:
        # 获取任务ID
        task_id = request.form.get('task_id')
        if not task_id:
            return jsonify({'error': '缺少任务ID'}), 400
        
        task = CheckinTask.query.get_or_404(int(task_id))
        
        # 检查是否已终止
        if task.is_terminated:
            return jsonify({'error': '任务已终止，无法继续打卡'}), 400
        
        # 检查当前日期是否在任务期限内（使用北京时间）
        today = get_beijing_date()
        if today < task.start_date:
            return jsonify({'error': '任务还未开始'}), 400
        
        if not task.is_long_term and today > task.end_date:
            return jsonify({'error': '任务已结束'}), 400
        
        # 检查今天是否已经打卡过（按频率判断）
        if task.frequency == 'daily':
            # 每天一次，检查今天是否已打卡
            existing_record = CheckinRecord.query.filter_by(
                task_id=task.id,
                checkin_date=today
            ).first()
            if existing_record:
                return jsonify({'error': '今天已经打卡过了'}), 400
        
        elif task.frequency == 'weekly':
            # 每周一次，检查本周是否已打卡
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            existing_record = CheckinRecord.query.filter(
                CheckinRecord.task_id == task.id,
                CheckinRecord.checkin_date >= week_start,
                CheckinRecord.checkin_date <= week_end
            ).first()
            if existing_record:
                return jsonify({'error': '本周已经打卡过了'}), 400
        
        elif task.frequency == 'monthly':
            # 每月一次，检查本月是否已打卡
            month_start = today.replace(day=1)
            if today.month == 12:
                month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            existing_record = CheckinRecord.query.filter(
                CheckinRecord.task_id == task.id,
                CheckinRecord.checkin_date >= month_start,
                CheckinRecord.checkin_date <= month_end
            ).first()
            if existing_record:
                return jsonify({'error': '本月已经打卡过了'}), 400
        
        elif task.frequency == 'custom' and task.custom_days:
            # 自定义天数，检查最近一次打卡是否满足间隔
            last_record = CheckinRecord.query.filter_by(task_id=task.id)\
                .order_by(CheckinRecord.checkin_date.desc()).first()
            if last_record:
                days_since_last = (today - last_record.checkin_date).days
                if days_since_last < task.custom_days:
                    remaining_days = task.custom_days - days_since_last
                    return jsonify({'error': f'距离上次打卡还需等待{remaining_days}天'}), 400
        
        # 获取备注
        note = request.form.get('note', '').strip()
        
        # 处理图片上传
        image_url = None
        image_path = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # 检查文件大小
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > 10 * 1024 * 1024:  # 10MB
                    return jsonify({'error': '图片大小不能超过10MB'}), 400
                
                # 生成唯一文件名
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                
                # 保存文件
                upload_path = get_upload_path()
                file_path = os.path.join(upload_path, unique_filename)
                file.save(file_path)
                
                image_url = f"/api/checkin/images/{unique_filename}"
                image_path = file_path
        
        # 创建打卡记录（today已在上面定义）
        record = CheckinRecord(
            task_id=task.id,
            checkin_date=today,
            note=note if note else None,
            image_url=image_url,
            image_path=image_path
        )
        
        # 更新任务统计
        task.checked_count += 1
        task.last_checkin_date = today
        
        db.session.add(record)
        db.session.commit()
        
        current_app.logger.info(f"打卡记录创建成功: Task {task.id}, Record {record.id}")
        
        return jsonify({
            'message': '打卡成功',
            'record': record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建打卡记录时出错: {e}")
        return jsonify({'error': f'打卡失败: {str(e)}'}), 500

@checkin_bp.route('/tasks/<int:task_id>/records', methods=['GET'])
def get_task_records(task_id):
    """获取任务的所有打卡记录"""
    try:
        task = CheckinTask.query.get_or_404(task_id)
        records = CheckinRecord.query.filter_by(task_id=task_id)\
            .order_by(CheckinRecord.checkin_date.desc()).all()
        
        return jsonify([record.to_dict() for record in records])
        
    except Exception as e:
        current_app.logger.error(f"获取打卡记录时出错: {e}")
        return jsonify({'error': '获取记录失败'}), 500

@checkin_bp.route('/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除打卡记录"""
    try:
        record = CheckinRecord.query.get_or_404(record_id)
        task = CheckinTask.query.get(record.task_id)
        
        # 删除图片文件
        if record.image_path and os.path.exists(record.image_path):
            try:
                os.remove(record.image_path)
            except Exception as e:
                current_app.logger.warning(f"删除图片文件失败: {e}")
        
        # 更新任务统计
        if task:
            task.checked_count = max(0, task.checked_count - 1)
            # 更新最后打卡日期
            last_record = CheckinRecord.query.filter_by(task_id=task.id)\
                .filter(CheckinRecord.id != record_id)\
                .order_by(CheckinRecord.checkin_date.desc()).first()
            task.last_checkin_date = last_record.checkin_date if last_record else None
        
        db.session.delete(record)
        db.session.commit()
        
        current_app.logger.info(f"打卡记录删除成功: Record {record_id}")
        return jsonify({'message': '记录删除成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除打卡记录时出错: {e}")
        return jsonify({'error': '删除失败'}), 500

@checkin_bp.route('/images/<filename>')
def get_image(filename):
    """获取打卡图片"""
    try:
        upload_path = get_upload_path()
        return send_from_directory(upload_path, filename)
    except Exception as e:
        current_app.logger.error(f"获取图片文件时出错: {e}")
        return jsonify({'error': '文件不存在'}), 404

