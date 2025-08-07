# models/blog.py
# **关键修改：从独立文件导入 db 实例**
from database import db  

class Post(db.Model):
    """
    Represents a blog post in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    excerpt = db.Column(db.Text, nullable=True) # Short summary of the post
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True) # URL for the cover image
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    views = db.Column(db.Integer, default=0) # 新增：阅读量字段，默认值为 0

    def __repr__(self):
        """
        String representation of the Post object.
        """
        return f'<Post {self.title}>'

    def to_dict(self):
        """
        Converts the Post object to a dictionary, suitable for JSON serialization.
        """
        return {
            'id': self.id,
            'title': self.title,
            'excerpt': self.excerpt,
            'content': self.content,
            'imageUrl': self.image_url, # Use camelCase for frontend consistency
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'views': self.views # 新增：包含 views 字段
        }
