# backend/models/set_type.py
from run import db # 从 run 导入新的数据库实例
from datetime import datetime

class SetType(db.Model):
    __bind_key__ = 'drive_stats' # 指定使用哪个数据库连接
    __tablename__ = 'set_types' # 定义表名

    set_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_name = db.Column(db.String(100), nullable=False, unique=True)
    two_piece_effect = db.Column(db.Text, nullable=True)
    four_piece_effect = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SetType {self.set_name}>'

    def to_dict(self):
        return {
            'set_id': self.set_id,
            'set_name': self.set_name,
            'two_piece_effect': self.two_piece_effect,
            'four_piece_effect': self.four_piece_effect,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }