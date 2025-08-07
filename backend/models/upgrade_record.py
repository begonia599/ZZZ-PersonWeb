# backend/models/upgrade_record.py
from database import db # 从 run 导入新的数据库实例
from datetime import datetime 

class UpgradeRecord(db.Model):
    __bind_key__ = 'drive_stats' # 指定使用哪个数据库连接
    __tablename__ = 'upgrade_records' # 定义表名

    upgrade_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive_pieces.drive_id', ondelete='CASCADE'), nullable=False)
    substat_id = db.Column(db.Integer, db.ForeignKey('drive_piece_substats.id', ondelete='CASCADE'), nullable=False)
    is_original = db.Column(db.Boolean, nullable=False, default=True) # BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否是原始词条'
    upgrade_count = db.Column(db.Integer, nullable=False, default=0) # INT NOT NULL DEFAULT 0 COMMENT '该词条被强化的次数'
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    # 定义关系
    drive_piece = db.relationship('DrivePiece', backref=db.backref('upgrade_records', lazy=True))
    substat_entry = db.relationship('DrivePieceSubstat', backref=db.backref('upgrade_records_substat', lazy=True))
    # 为避免 backref 名称冲突，为 substat_entry 关系使用了不同的 backref 名称

    def __repr__(self):
        return f'<UpgradeRecord {self.upgrade_id} (Drive: {self.drive_id}, Substat: {self.substat_id}, Count: {self.upgrade_count})>'

    def to_dict(self):
        # 通过关系访问关联对象的数据
        substat_name = None
        if self.substat_entry and self.substat_entry.stat_type:
            substat_name = self.substat_entry.stat_type.stat_name

        drive_position = None
        main_stat_name_of_drive = None
        set_name_of_drive = None
        if self.drive_piece:
            drive_position = self.drive_piece.position
            if self.drive_piece.main_stat_type:
                main_stat_name_of_drive = self.drive_piece.main_stat_type.stat_name
            if self.drive_piece.set_type:
                set_name_of_drive = self.drive_piece.set_type.set_name

        return {
            'upgrade_id': self.upgrade_id,
            'drive_id': self.drive_id,
            'substat_id': self.substat_id,
            'is_original': self.is_original,
            'upgrade_count': self.upgrade_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sub_stat_name': substat_name,
            'drive_position': drive_position,
            'main_stat_name_of_drive': main_stat_name_of_drive,
            'set_name_of_drive': set_name_of_drive,
        }