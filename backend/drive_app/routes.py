from flask import Blueprint, request, jsonify
from database import db  # 改为从 database.py 导入
from models.set_type import SetType
from models.stat_type import StatType
from models.drive_piece import DrivePiece, DrivePieceSubstat
from models.upgrade_record import UpgradeRecord
from sqlalchemy.orm import joinedload
from sqlalchemy import func, case, and_
from datetime import datetime
import random

# 创建一个蓝图实例，所有与驱动盘相关的路由都将注册到这个蓝图上
# url_prefix='/api/drive' 意味着所有路由都将以 /api/drive 开头
drive_bp = Blueprint('drive', __name__, url_prefix='/api/drive')


@drive_bp.route('/add', methods=['POST'])
def add_drive_piece():
    """
    添加新的驱动盘
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        # 验证必填字段
        required_fields = ['set_name', 'position', 'main_stat_name', 'substats']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 验证套装名称
        set_type = SetType.query.filter_by(set_name=data['set_name']).first()
        if not set_type:
            return jsonify({'error': f'未知的套装名称: {data["set_name"]}'}), 400

        # 验证主词条
        main_stat_type = StatType.query.filter_by(stat_name=data['main_stat_name']).first()
        if not main_stat_type:
            return jsonify({'error': f'未知的主词条: {data["main_stat_name"]}'}), 400

        # 验证副词条
        substats = data['substats']
        if not substats or len(substats) < 3 or len(substats) > 4:
            return jsonify({'error': '副词条数量必须在3-4个之间'}), 400

        substat_types = []
        for substat_name in substats:
            substat_type = StatType.query.filter_by(stat_name=substat_name).first()
            if not substat_type:
                return jsonify({'error': f'未知的副词条: {substat_name}'}), 400
            substat_types.append(substat_type)

        # 验证位置
        position = data['position']
        if not isinstance(position, int) or position < 1 or position > 6:
            return jsonify({'error': '位置必须是1-6之间的整数'}), 400

        # 创建驱动盘
        drive_piece = DrivePiece(
            set_id=set_type.set_id,
            position=position,
            main_stat_id=main_stat_type.stat_type_id,
            total_upgrades=0,
            substats=substats  # JSON格式存储
        )

        db.session.add(drive_piece)
        db.session.flush()  # 获取生成的 drive_id

        # 添加副词条记录
        for substat_type in substat_types:
            substat_entry = DrivePieceSubstat(
                drive_id=drive_piece.drive_id,
                stat_id=substat_type.stat_type_id
            )
            db.session.add(substat_entry)
            db.session.flush()  # 获取生成的 substat_id

            # 创建初始强化记录（所有词条都是原始的，强化次数为0）
            upgrade_record = UpgradeRecord(
                drive_id=drive_piece.drive_id,
                substat_id=substat_entry.id,
                is_original=True,
                upgrade_count=0
            )
            db.session.add(upgrade_record)

        db.session.commit()

        return jsonify({
            'message': '驱动盘添加成功',
            'drive': drive_piece.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '添加驱动盘失败', 'details': str(e)}), 500

@drive_bp.route('/pieces', methods=['GET'])
def get_drive_pieces():
    """
    获取驱动盘列表，支持分页
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 限制每页数量
        if per_page > 100:
            per_page = 100

        # 查询驱动盘，预加载相关数据
        query = DrivePiece.query.options(
            joinedload(DrivePiece.set_type),
            joinedload(DrivePiece.main_stat_type)
        ).order_by(DrivePiece.created_at.desc())

        paginated_result = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        drives = []
        for drive in paginated_result.items:
            # 分别查询副词条和强化记录，避免复杂JOIN导致的问题
            # 1. 先获取副词条信息
            substats_entries = db.session.query(
                DrivePieceSubstat, StatType.stat_name
            ).join(
                StatType, DrivePieceSubstat.stat_id == StatType.stat_type_id
            ).filter(
                DrivePieceSubstat.drive_id == drive.drive_id
            ).all()

            substats_with_levels = []
            for substat_entry, stat_name in substats_entries:
                # 2. 为每个副词条查询强化记录
                upgrade_record = UpgradeRecord.query.filter_by(
                    substat_id=substat_entry.id
                ).first()
                
                substats_with_levels.append({
                    'name': stat_name or '未知词条',
                    'upgrade_count': upgrade_record.upgrade_count if upgrade_record else 0,
                    'is_original': upgrade_record.is_original if upgrade_record else True,
                    'substat_id': substat_entry.id
                })

            drive_dict = drive.to_dict()
            drive_dict['substats_with_levels'] = substats_with_levels
            drives.append(drive_dict)

        return jsonify({
            'drives': drives,
            'pagination': {
                'current_page': paginated_result.page,
                'per_page': paginated_result.per_page,
                'total_items': paginated_result.total,
                'total_pages': paginated_result.pages,
                'has_next': paginated_result.has_next,
                'has_prev': paginated_result.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({'error': '获取驱动盘列表失败', 'details': str(e)}), 500

@drive_bp.route('/pieces/<int:drive_id>', methods=['GET'])
def get_drive_piece(drive_id):
    """
    获取单个驱动盘的详细信息
    """
    try:
        drive = DrivePiece.query.options(
            joinedload(DrivePiece.set_type),
            joinedload(DrivePiece.main_stat_type)
        ).get(drive_id)

        if not drive:
            return jsonify({'error': '驱动盘不存在'}), 404

        # 获取副词条及其强化信息（使用LEFT JOIN处理没有强化记录的情况）
        substats_query = db.session.query(
            DrivePieceSubstat,
            StatType.stat_name,
            UpgradeRecord.upgrade_count,
            UpgradeRecord.is_original
        ).join(
            StatType, DrivePieceSubstat.stat_id == StatType.stat_type_id
        ).outerjoin(
            UpgradeRecord, DrivePieceSubstat.id == UpgradeRecord.substat_id
        ).filter(
            DrivePieceSubstat.drive_id == drive_id
        ).all()

        substats_with_levels = []
        for substat_entry, stat_name, upgrade_count, is_original in substats_query:
            substats_with_levels.append({
                'name': stat_name,
                'upgrade_count': upgrade_count if upgrade_count is not None else 0,
                'is_original': is_original if is_original is not None else True,
                'substat_id': substat_entry.id
            })

        drive_dict = drive.to_dict()
        drive_dict['substats_with_levels'] = substats_with_levels

        return jsonify(drive_dict), 200

    except Exception as e:
        return jsonify({'error': '获取驱动盘信息失败', 'details': str(e)}), 500

@drive_bp.route('/pieces/<int:drive_id>', methods=['PUT'])
def update_drive_piece(drive_id):
    """
    更新驱动盘的词条信息
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        drive = DrivePiece.query.get(drive_id)
        if not drive:
            return jsonify({'error': '驱动盘不存在'}), 404

        # 更新主词条
        if 'main_stat_name' in data:
            main_stat_type = StatType.query.filter_by(stat_name=data['main_stat_name']).first()
            if not main_stat_type:
                return jsonify({'error': f'未知的主词条: {data["main_stat_name"]}'}), 400
            drive.main_stat_id = main_stat_type.stat_type_id

        # 更新副词条
        if 'substats' in data:
            new_substats = data['substats']
            if not new_substats or len(new_substats) < 1 or len(new_substats) > 4:
                return jsonify({'error': '副词条数量必须在1-4个之间'}), 400

            # 验证所有副词条
            new_substat_types = []
            for substat_name in new_substats:
                substat_type = StatType.query.filter_by(stat_name=substat_name).first()
                if not substat_type:
                    return jsonify({'error': f'未知的副词条: {substat_name}'}), 400
                new_substat_types.append(substat_type)

            # 删除旧的副词条记录和强化记录
            old_substat_entries = DrivePieceSubstat.query.filter_by(drive_id=drive_id).all()
            for entry in old_substat_entries:
                # 删除相关的强化记录
                UpgradeRecord.query.filter_by(substat_id=entry.id).delete()
                db.session.delete(entry)

            # 重置强化进度
            drive.total_upgrades = 0

            # 添加新的副词条记录
            for substat_type in new_substat_types:
                substat_entry = DrivePieceSubstat(
                    drive_id=drive_id,
                    stat_id=substat_type.stat_type_id
                )
                db.session.add(substat_entry)
                db.session.flush()

                # 创建新的强化记录
                upgrade_record = UpgradeRecord(
                    drive_id=drive_id,
                    substat_id=substat_entry.id,
                    is_original=True,
                    upgrade_count=0
                )
                db.session.add(upgrade_record)

            # 更新JSON字段
            drive.substats = new_substats

        db.session.commit()
        return jsonify({'message': '驱动盘更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新驱动盘失败', 'details': str(e)}), 500

@drive_bp.route('/pieces/<int:drive_id>/upgrade', methods=['POST'])
def upgrade_drive_piece(drive_id):
    """
    强化驱动盘词条
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        drive = DrivePiece.query.get(drive_id)
        if not drive:
            return jsonify({'error': '驱动盘不存在'}), 404

        # 检查是否还能强化
        if drive.total_upgrades >= 5:
            return jsonify({'error': '该驱动盘已强化满级'}), 400

        upgrade_type = data.get('upgrade_type')  # 'existing' 或 'new'
        new_substat_name = data.get('new_substat_name')  # 指定的新副词条名称
        
        current_substats = DrivePieceSubstat.query.filter_by(drive_id=drive_id).all()
        current_upgrades = drive.total_upgrades

        if upgrade_type == 'new':
            # 生成新副词条
            if len(current_substats) >= 4:
                return jsonify({'error': '副词条已满，无法生成新词条'}), 400

            # 如果指定了新副词条名称，使用指定的；否则随机选择
            if new_substat_name:
                # 验证指定的副词条是否有效
                new_stat = StatType.query.filter_by(stat_name=new_substat_name).first()
                if not new_stat:
                    return jsonify({'error': f'无效的副词条: {new_substat_name}'}), 400
                
                # 检查是否与主词条或现有副词条冲突
                existing_stat_ids = set([drive.main_stat_id] + [s.stat_id for s in current_substats])
                if new_stat.stat_type_id in existing_stat_ids:
                    return jsonify({'error': f'副词条 {new_substat_name} 已存在'}), 400
            else:
                # 获取所有可用的副词条类型（排除主词条和现有副词条）
                existing_stat_ids = set([drive.main_stat_id] + [s.stat_id for s in current_substats])
                available_stats = StatType.query.filter(
                    ~StatType.stat_type_id.in_(existing_stat_ids)
                ).all()

                if not available_stats:
                    return jsonify({'error': '没有可用的新副词条'}), 400

                # 随机选择一个新副词条
                new_stat = random.choice(available_stats)

            # 创建新的副词条记录
            new_substat_entry = DrivePieceSubstat(
                drive_id=drive_id,
                stat_id=new_stat.stat_type_id
            )
            db.session.add(new_substat_entry)
            db.session.flush()

            # 创建强化记录
            upgrade_record = UpgradeRecord(
                drive_id=drive_id,
                substat_id=new_substat_entry.id,
                is_original=False,  # 新生成的词条不是原始词条
                upgrade_count=0 if current_upgrades == 0 and len(current_substats) == 3 else 1
            )
            db.session.add(upgrade_record)

            # 更新驱动盘JSON数据（如果存在的话）
            try:
                current_substats_names = []
                for substat in current_substats:
                    stat = StatType.query.get(substat.stat_id)
                    if stat:
                        current_substats_names.append(stat.stat_name)
                
                updated_substats = current_substats_names + [new_stat.stat_name]
                drive.substats = updated_substats
            except Exception as e:
                # 如果JSON字段更新失败，不影响主要功能
                print(f"更新JSON字段失败: {e}")
                pass

            upgrade_result = {
                'type': 'new_substat',
                'new_substat': new_stat.stat_name,
                'upgrade_count': upgrade_record.upgrade_count
            }

        elif upgrade_type == 'existing':
            # 强化现有副词条
            substat_id = data.get('substat_id')
            if not substat_id:
                return jsonify({'error': '请选择要强化的副词条'}), 400

            # 验证副词条是否存在
            substat_entry = DrivePieceSubstat.query.get(substat_id)
            if not substat_entry or substat_entry.drive_id != drive_id:
                return jsonify({'error': '副词条不存在'}), 400

            # 查找或创建强化记录
            upgrade_record = UpgradeRecord.query.filter_by(
                drive_id=drive_id,
                substat_id=substat_id
            ).first()

            if not upgrade_record:
                # 如果没有强化记录，创建一个新的
                upgrade_record = UpgradeRecord(
                    drive_id=drive_id,
                    substat_id=substat_id,
                    is_original=True,  # 假设是原始词条
                    upgrade_count=0
                )
                db.session.add(upgrade_record)
                db.session.flush()  # 确保记录被保存

            # 增加强化次数
            upgrade_record.upgrade_count += 1

            # 获取副词条名称用于返回
            stat_type = StatType.query.get(substat_entry.stat_id)

            upgrade_result = {
                'type': 'upgrade_existing',
                'substat_name': stat_type.stat_name,
                'new_upgrade_count': upgrade_record.upgrade_count
            }

        else:
            return jsonify({'error': '无效的强化类型'}), 400

        # 更新总强化次数
        drive.total_upgrades += 1

        db.session.commit()

        return jsonify({
            'message': '强化成功',
            'result': upgrade_result,
            'new_total_upgrades': drive.total_upgrades
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '强化失败', 'details': str(e)}), 500

@drive_bp.route('/pieces/<int:drive_id>/downgrade', methods=['POST'])
def downgrade_drive_piece(drive_id):
    """
    降低驱动盘副词条等级
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        drive = DrivePiece.query.get(drive_id)
        if not drive:
            return jsonify({'error': '驱动盘不存在'}), 404

        substat_id = data.get('substat_id')
        if not substat_id:
            return jsonify({'error': '请指定要降级的副词条'}), 400

        # 验证副词条是否存在
        substat_entry = DrivePieceSubstat.query.get(substat_id)
        if not substat_entry or substat_entry.drive_id != drive_id:
            return jsonify({'error': '副词条不存在'}), 400

        # 查找强化记录
        upgrade_record = UpgradeRecord.query.filter_by(
            drive_id=drive_id,
            substat_id=substat_id
        ).first()

        if not upgrade_record:
            return jsonify({'error': '该副词条还没有进行过强化'}), 400

        # 检查是否可以降级
        if upgrade_record.upgrade_count <= 0:
            return jsonify({'error': '该副词条已经是最低等级'}), 400

        # 减少强化次数
        upgrade_record.upgrade_count -= 1
        
        # 减少总强化次数
        drive.total_upgrades -= 1

        # 获取副词条名称用于返回
        substat_entry = DrivePieceSubstat.query.get(substat_id)
        stat_type = StatType.query.get(substat_entry.stat_id)

        db.session.commit()

        return jsonify({
            'message': '降级成功',
            'result': {
                'type': 'downgrade',
                'substat_name': stat_type.stat_name,
                'new_upgrade_count': upgrade_record.upgrade_count
            },
            'new_total_upgrades': drive.total_upgrades
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '降级失败', 'details': str(e)}), 500

@drive_bp.route('/pieces/<int:drive_id>', methods=['DELETE'])
def delete_drive_piece(drive_id):
    """
    删除驱动盘
    """
    try:
        drive = DrivePiece.query.get(drive_id)
        if not drive:
            return jsonify({'error': '驱动盘不存在'}), 404

        # 删除相关的强化记录
        UpgradeRecord.query.filter_by(drive_id=drive_id).delete()

        # 删除相关的副词条记录
        DrivePieceSubstat.query.filter_by(drive_id=drive_id).delete()

        # 删除驱动盘
        db.session.delete(drive)

        db.session.commit()
        return jsonify({'message': '驱动盘删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除驱动盘失败', 'details': str(e)}), 500

@drive_bp.route('/set-types', methods=['GET'])
def get_set_types():
    """
    获取所有套装类型
    """
    try:
        set_types = SetType.query.all()
        return jsonify([set_type.set_name for set_type in set_types]), 200
    except Exception as e:
        return jsonify({'error': '获取套装类型失败', 'details': str(e)}), 500

@drive_bp.route('/stat-types', methods=['GET'])
def get_stat_types():
    """
    获取所有词条类型
    """
    try:
        stat_types = StatType.query.all()
        return jsonify([stat_type.stat_name for stat_type in stat_types]), 200
    except Exception as e:
        return jsonify({'error': '获取词条类型失败', 'details': str(e)}), 500

@drive_bp.route('/stats', methods=['GET'])
def get_drive_stats():
    """
    获取驱动盘统计信息
    """
    try:
        # 总数统计
        total_pieces = DrivePiece.query.count()
        
        # 按位置分布统计
        position_stats = db.session.query(
            DrivePiece.position,
            func.count(DrivePiece.drive_id).label('count')
        ).group_by(DrivePiece.position).all()
        
        position_distribution = {f"{pos}号位": count for pos, count in position_stats}
        
        # 按套装分布统计
        set_stats = db.session.query(
            SetType.set_name,
            func.count(DrivePiece.drive_id).label('count')
        ).join(
            DrivePiece, SetType.set_id == DrivePiece.set_id
        ).group_by(SetType.set_name).all()
        
        set_distribution = {set_name: count for set_name, count in set_stats}
        
        # 主词条分布统计
        main_stat_stats = db.session.query(
            StatType.stat_name,
            func.count(DrivePiece.drive_id).label('count')
        ).join(
            DrivePiece, StatType.stat_type_id == DrivePiece.main_stat_id
        ).group_by(StatType.stat_name).all()
        
        main_stat_distribution = {stat_name: count for stat_name, count in main_stat_stats}
        
        # 副词条出现频率统计
        substat_stats = db.session.query(
            StatType.stat_name,
            func.count(DrivePieceSubstat.id).label('count')
        ).join(
            DrivePieceSubstat, StatType.stat_type_id == DrivePieceSubstat.stat_id
        ).group_by(StatType.stat_name).all()
        
        substat_frequency = {
            stat_name: {'count': count, 'percentage': round((count / total_pieces * 100) if total_pieces > 0 else 0, 2)}
            for stat_name, count in substat_stats
        }
        
        # 强化分布统计
        upgrade_stats = db.session.query(
            DrivePiece.total_upgrades,
            func.count(DrivePiece.drive_id).label('count')
        ).group_by(DrivePiece.total_upgrades).all()
        
        upgrade_distribution = {f"+{upgrade_level}": count for upgrade_level, count in upgrade_stats}
        
        # 计算前端需要的额外统计数据
        total_sets = len(set_distribution)
        total_substats = sum([item['count'] for item in substat_frequency.values()])
        avg_substats = round(total_substats / total_pieces, 1) if total_pieces > 0 else 0
        
        # 按位置分组主词条统计
        main_stats_by_position = {}
        for pos in range(1, 7):  # 1-6号位
            pos_stats = db.session.query(
                StatType.stat_name,
                func.count(DrivePiece.drive_id).label('count')
            ).join(
                DrivePiece, StatType.stat_type_id == DrivePiece.main_stat_id
            ).filter(
                DrivePiece.position == pos
            ).group_by(StatType.stat_name).all()
            
            main_stats_by_position[f"{pos}号位"] = {stat_name: count for stat_name, count in pos_stats}
        
        # 副词条数量分布统计
        substat_count_stats = db.session.query(
            func.count(DrivePieceSubstat.stat_id).label('substat_count'),
            func.count(func.distinct(DrivePieceSubstat.drive_id)).label('drive_count')
        ).group_by(DrivePieceSubstat.drive_id).subquery()
        
        substat_count_distribution = db.session.query(
            substat_count_stats.c.substat_count,
            func.count(substat_count_stats.c.drive_count).label('count')
        ).group_by(substat_count_stats.c.substat_count).all()
        
        substat_count_dist = {int(substat_count): int(count) for substat_count, count in substat_count_distribution}

        return jsonify({
            'total_pieces': total_pieces,
            'total_sets': total_sets,
            'avg_substats': avg_substats,
            'position_distribution': position_distribution,
            'set_distribution': set_distribution,
            'main_stats': main_stats_by_position,
            'substat_frequency': substat_frequency,
            'substat_count_distribution': substat_count_dist,
            'upgrade_distribution': upgrade_distribution,
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取统计数据失败', 'details': str(e)}), 500

@drive_bp.route('/stats/pairing', methods=['POST'])
def calculate_pairing_probability():
    """
    计算词条配对的理论概率和实际概率
    """
    try:
        data = request.get_json()
        if not data or 'selected_stats' not in data:
            return jsonify({'error': '请求参数错误'}), 400
        
        selected_stats = data['selected_stats']
        if not selected_stats or len(selected_stats) == 0:
            return jsonify({'error': '请至少选择一个词条'}), 400
        
        if len(selected_stats) > 4:
            return jsonify({'error': '最多只能选择4个词条'}), 400
        
        # 验证词条是否存在
        stat_types = StatType.query.filter(StatType.stat_name.in_(selected_stats)).all()
        if len(stat_types) != len(selected_stats):
            return jsonify({'error': '选择的词条中包含不存在的词条'}), 400
        
        stat_id_map = {stat.stat_name: stat.stat_type_id for stat in stat_types}
        selected_stat_ids = [stat_id_map[name] for name in selected_stats]
        
        # 1. 计算理论概率
        total_pieces = DrivePiece.query.count()
        if total_pieces == 0:
            return jsonify({'error': '暂无驱动盘数据'}), 400
        
        # 获取各个词条的独立概率
        individual_probabilities = {}
        for stat_name in selected_stats:
            count = db.session.query(func.count(func.distinct(DrivePieceSubstat.drive_id))).join(
                StatType, DrivePieceSubstat.stat_id == StatType.stat_type_id
            ).filter(StatType.stat_name == stat_name).scalar() or 0
            
            probability = (count / total_pieces) if total_pieces > 0 else 0
            individual_probabilities[stat_name] = probability
        
        # 计算理论概率（假设各词条独立出现）
        theoretical_probability = 1.0
        for prob in individual_probabilities.values():
            theoretical_probability *= prob
        
        theoretical_percentage = round(theoretical_probability * 100, 4)
        
        # 2. 计算实际概率
        # 找出同时拥有所有选定词条的驱动盘
        # 使用子查询来统计每个驱动盘有多少个选定的词条
        subquery = db.session.query(
            DrivePieceSubstat.drive_id,
            func.count(DrivePieceSubstat.stat_id).label('matching_count')
        ).filter(
            DrivePieceSubstat.stat_id.in_(selected_stat_ids)
        ).group_by(DrivePieceSubstat.drive_id).subquery()
        
        # 找出拥有全部选定词条的驱动盘数量
        matching_pieces = db.session.query(subquery).filter(
            subquery.c.matching_count == len(selected_stats)
        ).count()
        
        actual_probability = (matching_pieces / total_pieces) if total_pieces > 0 else 0
        actual_percentage = round(actual_probability * 100, 4)
        
        # 3. 计算差异和其他统计信息
        difference = round(actual_percentage - theoretical_percentage, 4)
        expectation = round(1 / actual_probability) if actual_probability > 0 else 0
        
        # 4. 获取详细匹配信息（可选，用于调试）
        matching_drives = []
        if matching_pieces > 0 and matching_pieces <= 20:  # 如果匹配数量不多，提供详细信息
            matching_drive_ids = db.session.query(subquery.c.drive_id).filter(
                subquery.c.matching_count == len(selected_stats)
            ).all()
            
            matching_drives = db.session.query(DrivePiece).filter(
                DrivePiece.drive_id.in_([drive_id[0] for drive_id in matching_drive_ids])
            ).options(
                joinedload(DrivePiece.set_type),
                joinedload(DrivePiece.main_stat_type)
            ).all()
        
        result = {
            'theoretical': theoretical_percentage,
            'actual': actual_percentage,
            'difference': difference,
            'matchCount': matching_pieces,
            'totalPieces': total_pieces,
            'expectation': expectation,
            'individual_probabilities': {
                stat_name: round(prob * 100, 2) 
                for stat_name, prob in individual_probabilities.items()
            },
            'selected_stats': selected_stats
        }
        
        # 如果匹配数量较少，添加详细匹配信息
        if matching_drives:
            result['matching_examples'] = [
                {
                    'drive_id': drive.drive_id,
                    'set_name': drive.set_type.set_name if drive.set_type else '未知',
                    'position': drive.position,
                    'main_stat': drive.main_stat_type.stat_name if drive.main_stat_type else '未知'
                }
                for drive in matching_drives[:10]  # 最多返回10个示例
            ]
        
        return jsonify(result), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '计算配对概率失败', 'details': str(e)}), 500