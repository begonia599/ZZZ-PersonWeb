# backend/models/stat_type.py
from database import db # 从 run 导入新的数据库实例
from datetime import datetime

class StatType(db.Model):
    __bind_key__ = 'drive_stats' # 指定使用哪个数据库连接
    __tablename__ = 'stat_types' # 定义表名

    stat_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # AUTO_INCREMENT 自动处理
    stat_name = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    def __repr__(self):
        return f'<StatType {self.stat_name}>'

    def to_dict(self):
        return {
            'stat_type_id': self.stat_type_id,
            'stat_name': self.stat_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }