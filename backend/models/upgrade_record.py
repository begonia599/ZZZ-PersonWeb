# backend/models/upgrade_record.py
from database import db # 从 run 导入新的数据库实例
from datetime import datetime 

class UpgradeRecord(db.Model):
    __bind_key__ = 'drive_stats' # 指定使用哪个数据库连接
    __tablename__ = 'upgrade_records' # 定义表名

    upgrade_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive_pieces.drive_id', ondelete='CASCADE'), nullable=False)
    substat_id = db.Column(db.Integer, db.ForeignKey('drive_piece_substats.id', ondelete='CASCADE'), nullable=False)
    is_original = db.Column(db.Boolean, nullable=False, default=True)  # 是否是原始词条
    upgrade_count = db.Column(db.Integer, nullable=False, default=0)  # 强化次数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    drive_piece = db.relationship('DrivePiece', backref=db.backref('upgrade_records', lazy=True, cascade='all, delete-orphan'))
    substat_entry = db.relationship('DrivePieceSubstat', backref=db.backref('upgrade_record', lazy=True, cascade='all, delete-orphan'))

    # 确保每个副词条只有一个强化记录
    __table_args__ = (
        db.UniqueConstraint('drive_id', 'substat_id', name='unique_drive_substat_upgrade'),
    )

    def __repr__(self):
        return f'<UpgradeRecord {self.upgrade_id}: Drive {self.drive_id} - Substat {self.substat_id} (+{self.upgrade_count})>'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'upgrade_id': self.upgrade_id,
            'drive_id': self.drive_id,
            'substat_id': self.substat_id,
            'is_original': self.is_original,
            'upgrade_count': self.upgrade_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }