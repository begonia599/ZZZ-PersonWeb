from flask import Blueprint, request, jsonify
from database import db  # 改为从 database.py 导入
from models.set_type import SetType
from models.stat_type import StatType
from models.drive_piece import DrivePiece, DrivePieceSubstat
from sqlalchemy.orm import joinedload
from datetime import datetime

# 创建一个蓝图实例，所有与驱动盘相关的路由都将注册到这个蓝图上
# url_prefix='/api/drive' 意味着所有路由都将以 /api/drive 开头
drive_bp = Blueprint('drive', __name__, url_prefix='/api/drive')

@drive_bp.route('/add', methods=['POST'])
def add_drive_piece():
    """
    接收用户输入的驱动盘信息，并将其存入数据库。
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体必须是JSON格式"}), 400

    set_name = data.get('set_name')
    position = data.get('position')
    main_stat_name = data.get('main_stat_name')
    substats_list = data.get('substats', [])
    
    # === 数据校验 ===
    if not all([set_name, position, main_stat_name]):
        return jsonify({"error": "缺少必要的字段：set_name, position, main_stat_name"}), 400

    if not isinstance(position, int) or not (1 <= position <= 6):
        return jsonify({"error": "位置字段 'position' 必须是1-6之间的整数"}), 400

    try:
        # === 1. 查找套装和词条的ID ===
        set_type = SetType.query.filter_by(set_name=set_name).first()
        main_stat_type = StatType.query.filter_by(stat_name=main_stat_name).first()

        if not set_type:
            return jsonify({"error": f"套装 '{set_name}' 不存在"}), 400
        if not main_stat_type:
            return jsonify({"error": f"主词条 '{main_stat_name}' 不存在"}), 400

        # === 2. 创建驱动盘记录 ===
        new_drive_piece = DrivePiece(
            set_id=set_type.set_id,
            position=position,
            main_stat_id=main_stat_type.stat_type_id
        )
        db.session.add(new_drive_piece)
        db.session.flush()  # 立即获取新记录的 drive_id

        # === 3. 创建副词条关联记录 ===
        unique_substat_ids = set()
        for substat_name in substats_list:
            substat_type = StatType.query.filter_by(stat_name=substat_name).first()
            if not substat_type:
                return jsonify({"error": f"副词条 '{substat_name}' 不存在"}), 400
            
            # 检查副词条是否与主词条重复
            if substat_type.stat_type_id == main_stat_type.stat_type_id:
                return jsonify({"error": f"副词条 '{substat_name}' 不能与主词条重复"}), 400
            
            # 检查副词条列表中是否有重复
            if substat_type.stat_type_id in unique_substat_ids:
                return jsonify({"error": f"副词条 '{substat_name}' 重复"}), 400
            
            unique_substat_ids.add(substat_type.stat_type_id)
            
            new_substat_link = DrivePieceSubstat(
                drive_id=new_drive_piece.drive_id,
                stat_id=substat_type.stat_type_id
            )
            db.session.add(new_substat_link)

        db.session.commit()

        return jsonify({
            "drive_id": new_drive_piece.drive_id, 
            "message": "驱动盘信息添加成功"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "添加驱动盘数据失败", "details": str(e)}), 500


@drive_bp.route('/pieces', methods=['GET'])
def get_drive_pieces():
    """
    获取所有驱动盘的列表，包括套装、主词条和副词条信息。
    """
    try:
        # 使用 SQLAlchemy 的 joinedload 优化查询，一次性获取所有关联数据
        # 避免 N+1 查询问题
        drive_pieces = DrivePiece.query.options(
            joinedload(DrivePiece.set_type),
            joinedload(DrivePiece.main_stat_type),
            joinedload(DrivePiece.substats).joinedload(DrivePieceSubstat.stat_type)
        ).order_by(DrivePiece.created_at.desc()).all()

        # 格式化数据以供前端使用
        result = []
        for piece in drive_pieces:
            # 确保 substats 关系已加载且不为空
            substats_list = [sub.stat_type.stat_name for sub in piece.substats] if piece.substats else []
            
            # 由于可能存在空值，需要添加安全检查
            set_name = piece.set_type.set_name if piece.set_type else '未知套装'
            main_stat_name = piece.main_stat_type.stat_name if piece.main_stat_type else '未知词条'

            result.append({
                'drive_id': piece.drive_id,
                'set_name': set_name,
                'position': piece.position,
                'main_stat_name': main_stat_name,
                'substats': substats_list,
                'created_at': piece.created_at.isoformat() if piece.created_at else None
            })

        return jsonify(result), 200

    except Exception as e:
        # 在出现异常时回滚会话，并返回错误信息
        db.session.rollback()
        return jsonify({'error': '获取驱动盘数据失败', 'details': str(e)}), 500

@drive_bp.route('/set-types', methods=['GET'])
def get_set_types():
    """
    获取所有套装类型列表
    """
    try:
        set_types = SetType.query.all()
        result = [set_type.set_name for set_type in set_types]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': '获取套装数据失败', 'details': str(e)}), 500

@drive_bp.route('/stat-types', methods=['GET'])
def get_stat_types():
    """
    获取所有词条类型列表
    """
    try:
        stat_types = StatType.query.all()
        result = [stat_type.stat_name for stat_type in stat_types]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': '获取词条数据失败', 'details': str(e)}), 500