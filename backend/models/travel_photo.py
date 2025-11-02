# models/travel_photo.py
from database import db
from datetime import datetime, timedelta, timezone

# 北京时区（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))

def get_beijing_now():
    """获取北京时间的当前时间"""
    return datetime.now(BEIJING_TZ)

class TravelPhoto(db.Model):
    """
    Represents a travel photo in the database.
    """
    __bind_key__ = 'travel_db'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=get_beijing_now)
    updated_at = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)

    def __repr__(self):
        """
        String representation of the TravelPhoto object.
        """
        return f'<TravelPhoto {self.title}>'

    def to_dict(self):
        """
        Converts the TravelPhoto object to a dictionary, suitable for JSON serialization.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'url': self.url,
            'thumbnail_url': self.thumbnail_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

