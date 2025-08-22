from run import create_app
from models.drive_piece import DrivePiece, DrivePieceSubstat
from models.stat_type import StatType
from models.upgrade_record import UpgradeRecord
from database import db

app = create_app()

with app.app_context():
    print("🧪 测试修复后的路由逻辑...")
    
    # 测试修复后的JOIN查询（现在使用LEFT JOIN）
    drive_id = 1
    print(f"测试驱动盘 ID: {drive_id}")
    
    # 模拟 get_drive_piece 路由中的查询
    substats_query = db.session.query(
        DrivePieceSubstat,
        StatType.stat_name,
        UpgradeRecord.upgrade_count,
        UpgradeRecord.is_original
    ).join(
        StatType, DrivePieceSubstat.stat_id == StatType.stat_type_id
    ).outerjoin(  # 使用LEFT JOIN
        UpgradeRecord, DrivePieceSubstat.id == UpgradeRecord.substat_id
    ).filter(
        DrivePieceSubstat.drive_id == drive_id
    ).all()
    
    print(f"\n🔄 LEFT JOIN查询结果数: {len(substats_query)}")
    
    substats_with_levels = []
    for substat_entry, stat_name, upgrade_count, is_original in substats_query:
        substat_info = {
            'name': stat_name,
            'upgrade_count': upgrade_count if upgrade_count is not None else 0,
            'is_original': is_original if is_original is not None else True,
            'substat_id': substat_entry.id
        }
        substats_with_levels.append(substat_info)
        print(f"  ✓ {stat_name}: +{substat_info['upgrade_count']} ({'原始' if substat_info['is_original'] else '新增'})")
    
    # 测试一个有强化记录的驱动盘
    print(f"\n🧪 测试有强化记录的驱动盘 (ID: 13):")
    substats_query_13 = db.session.query(
        DrivePieceSubstat,
        StatType.stat_name,
        UpgradeRecord.upgrade_count,
        UpgradeRecord.is_original
    ).join(
        StatType, DrivePieceSubstat.stat_id == StatType.stat_type_id
    ).outerjoin(
        UpgradeRecord, DrivePieceSubstat.id == UpgradeRecord.substat_id
    ).filter(
        DrivePieceSubstat.drive_id == 13
    ).all()
    
    print(f"  LEFT JOIN查询结果数: {len(substats_query_13)}")
    for substat_entry, stat_name, upgrade_count, is_original in substats_query_13:
        upgrade_count = upgrade_count if upgrade_count is not None else 0
        is_original = is_original if is_original is not None else True
        print(f"    ✓ {stat_name}: +{upgrade_count} ({'原始' if is_original else '新增'})")
    
    # 测试统计查询
    print(f"\n📈 测试统计查询:")
    try:
        total_pieces = DrivePiece.query.count()
        print(f"  驱动盘总数: {total_pieces}")
        
        # 位置分布
        position_stats = db.session.query(
            DrivePiece.position,
            db.func.count(DrivePiece.drive_id).label('count')
        ).group_by(DrivePiece.position).all()
        
        print(f"  位置分布: {len(position_stats)} 个位置")
        for pos, count in position_stats[:3]:
            print(f"    {pos}号位: {count} 个")
            
    except Exception as e:
        print(f"  ❌ 统计查询失败: {e}")
    
    print(f"\n✅ 路由测试完成")



