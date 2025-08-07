# backend/models/drive_piece.py
from database import db # 从 run 导入新的数据库实例
from datetime import datetime
# 导入相关联的模型 (StatType, SetType)
# 确保 StatType 和 SetType 也在 drive_stats_db 上下文中
# 它们会通过 from models import stat_type, set_type 被 run.py 导入
# 所以这里无需再次导入 db.Model 依赖
from .stat_type import StatType # 如果 stat_type.py 在同一目录且需要显式导入
from .set_type import SetType   # 如果 set_type.py 在同一目录且需要显式导入

class DrivePiece(db.Model):
    __bind_key__ = 'drive_stats' # 指定使用哪个数据库连接
    __tablename__ = 'drive_pieces' # 定义表名

    drive_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_id = db.Column(db.Integer, db.ForeignKey('set_types.set_id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    main_stat_id = db.Column(db.Integer, db.ForeignKey('stat_types.stat_type_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 定义关系，通过 set_id 和 main_stat_id 关联到 SetType 和 StatType
    set_type = db.relationship('SetType', backref=db.backref('drive_pieces', lazy=True))
    main_stat_type = db.relationship('StatType', backref=db.backref('main_drive_pieces', lazy=True))

    # CHECK 约束: position BETWEEN 1 AND 6
    __table_args__ = (
        db.CheckConstraint('position >= 1 AND position <= 6', name='position_check'),
    )

    def __repr__(self):
        return f'<DrivePiece {self.drive_id} (Set: {self.set_id}, Pos: {self.position}, MainStat: {self.main_stat_id})>'

    def to_dict(self, include_substats=False):
        data = {
            'drive_id': self.drive_id,
            'set_id': self.set_id,
            'set_name': self.set_type.set_name if self.set_type else None, # 通过关系获取套装名称
            'position': self.position,
            'main_stat_id': self.main_stat_id,
            'main_stat_name': self.main_stat_type.stat_name if self.main_stat_type else None, # 通过关系获取主词条名称
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_substats:
            # 加载副词条，并通过它们的 to_dict 方法序列化
            data['substats'] = [sub.to_dict() for sub in self.substats] if self.substats else []
        return data


class DrivePieceSubstat(db.Model):
    __bind_key__ = 'drive_stats'
    __tablename__ = 'drive_piece_substats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive_pieces.drive_id', ondelete='CASCADE'), nullable=False)
    stat_id = db.Column(db.Integer, db.ForeignKey('stat_types.stat_type_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 定义关系
    # backref='substats' 会在 DrivePiece 模型上添加一个 'substats' 属性，
    # 允许我们访问一个驱动盘的所有关联副词条
    drive_piece = db.relationship('DrivePiece', backref=db.backref('substats', cascade="all, delete-orphan", lazy=True))
    stat_type = db.relationship('StatType', backref=db.backref('drive_piece_substats', lazy=True))

    # UNIQUE KEY (drive_id, stat_id)
    __table_args__ = (
        db.UniqueConstraint('drive_id', 'stat_id', name='_drive_stat_uc'),
    )

    def __repr__(self):
        return f'<DrivePieceSubstat {self.id} (Drive: {self.drive_id}, Stat: {self.stat_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'drive_id': self.drive_id,
            'stat_id': self.stat_id,
            'stat_name': self.stat_type.stat_name if self.stat_type else None, # 通过关系获取词条名称
            'created_at': self.created_at.isoformat() if self.created_at else None
        }