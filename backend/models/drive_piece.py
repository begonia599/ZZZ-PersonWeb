# backend/models/drive_piece.py
from database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON  # 如果使用 PostgreSQL，可以直接使用 JSON 类型

class DrivePiece(db.Model):
    __bind_key__ = 'drive_stats'
    __tablename__ = 'drive_pieces'

    drive_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_id = db.Column(db.Integer, db.ForeignKey('set_types.set_id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    main_stat_id = db.Column(db.Integer, db.ForeignKey('stat_types.stat_type_id'), nullable=False)
    main_stat_level = db.Column(db.Integer, default=15)  # 主词条等级，默认15
    total_upgrades = db.Column(db.Integer, default=0)  # 强化点数
    substats = db.Column(db.JSON)  # 以JSON格式存储副词条列表
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    set_type = db.relationship('SetType', backref=db.backref('drive_pieces', lazy=True))
    main_stat_type = db.relationship('StatType', backref=db.backref('main_stat_pieces', lazy=True))
    
    def __repr__(self):
        return f'<DrivePiece {self.drive_id}: {self.position}号位>'

    def to_dict(self):
        """转换为字典格式，便于JSON序列化"""
        return {
            'drive_id': self.drive_id,
            'set_name': self.set_type.set_name if self.set_type else None,
            'position': self.position,
            'main_stat_name': self.main_stat_type.stat_name if self.main_stat_type else None,
            'main_stat_level': self.main_stat_level,
            'total_upgrades': self.total_upgrades,
            'substats': self.substats or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DrivePieceSubstat(db.Model):
    """驱动盘副词条关联表"""
    __bind_key__ = 'drive_stats'
    __tablename__ = 'drive_piece_substats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive_pieces.drive_id', ondelete='CASCADE'), nullable=False)
    stat_id = db.Column(db.Integer, db.ForeignKey('stat_types.stat_type_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系定义
    drive_piece = db.relationship('DrivePiece', backref=db.backref('substat_entries', lazy=True, cascade='all, delete-orphan'))
    stat_type = db.relationship('StatType', backref=db.backref('substat_pieces', lazy=True))

    # 确保同一个驱动盘不会有重复的副词条
    __table_args__ = (
        db.UniqueConstraint('drive_id', 'stat_id', name='unique_drive_substat'),
    )

    def __repr__(self):
        return f'<DrivePieceSubstat {self.id}: Drive {self.drive_id} - Stat {self.stat_id}>'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'drive_id': self.drive_id,
            'stat_id': self.stat_id,
            'stat_name': self.stat_type.stat_name if self.stat_type else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }