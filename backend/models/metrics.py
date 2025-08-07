# backend/models/metrics.py
from database import db
from datetime import datetime # 确保 datetime 已导入

class WebsiteMetrics(db.Model):
    """
    表示网站范围的指标，如访问人数和启动时间。
    此表中应该只有一行。
    """
    id = db.Column(db.Integer, primary_key=True, default=1) # 固定 ID 用于单行
    visitor_count = db.Column(db.Integer, default=0, nullable=False)
    startup_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) # 使用 datetime.utcnow
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # 使用 datetime.utcnow

    def __repr__(self):
        return f'<WebsiteMetrics visitor_count={self.visitor_count}>'

    def to_dict(self):
        return {
            'id': self.id,
            'visitorCount': self.visitor_count,
            'startupTime': self.startup_time.isoformat() if self.startup_time else None,
            'lastUpdated': self.last_updated.isoformat() if self.last_updated else None,
        }

