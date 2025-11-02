# models/checkin.py
from database import db
from datetime import datetime, timedelta, timezone

# 北京时区（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))

def get_beijing_now():
    """获取北京时间的当前时间"""
    return datetime.now(BEIJING_TZ)

class CheckinTask(db.Model):
    """
    Represents a check-in task in the database.
    """
    __bind_key__ = 'checkin_db'
    __tablename__ = 'checkin_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly, custom
    custom_days = db.Column(db.Integer, nullable=True)  # for custom frequency
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_count = db.Column(db.Integer, nullable=False, default=0)
    checked_count = db.Column(db.Integer, nullable=False, default=0)
    last_checkin_date = db.Column(db.Date, nullable=True)
    is_long_term = db.Column(db.Boolean, nullable=False, default=False)
    is_terminated = db.Column(db.Boolean, nullable=False, default=False)
    duration = db.Column(db.Integer, nullable=True)  # duration in days
    created_at = db.Column(db.DateTime, default=get_beijing_now)
    updated_at = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)
    
    # Relationship
    records = db.relationship('CheckinRecord', backref='task', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<CheckinTask {self.title}>'

    def to_dict(self):
        # 处理时区信息
        def format_datetime(dt):
            if dt:
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=BEIJING_TZ).isoformat()
                return dt.isoformat()
            return None
        
        return {
            'id': self.id,
            'title': self.title,
            'frequency': self.frequency,
            'custom_days': self.custom_days,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_count': self.total_count,
            'checked_count': self.checked_count,
            'last_checkin_date': self.last_checkin_date.isoformat() if self.last_checkin_date else None,
            'is_long_term': self.is_long_term,
            'is_terminated': self.is_terminated,
            'duration': self.duration,
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at)
        }


class CheckinRecord(db.Model):
    """
    Represents a check-in record in the database.
    """
    __bind_key__ = 'checkin_db'
    __tablename__ = 'checkin_records'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('checkin_tasks.id'), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    image_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=get_beijing_now)

    def __repr__(self):
        return f'<CheckinRecord {self.id}>'

    def to_dict(self):
        # 处理 created_at 的时区信息
        created_at_str = None
        if self.created_at:
            # 如果是 naive datetime，添加北京时区
            if self.created_at.tzinfo is None:
                created_at_aware = self.created_at.replace(tzinfo=BEIJING_TZ)
                created_at_str = created_at_aware.isoformat()
            else:
                created_at_str = self.created_at.isoformat()
        
        return {
            'id': self.id,
            'task_id': self.task_id,
            'checkin_date': self.checkin_date.isoformat() if self.checkin_date else None,
            'note': self.note,
            'image_url': self.image_url,
            'created_at': created_at_str
        }

