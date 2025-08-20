# backend/models/set_type.py
from database import db

class SetType(db.Model):
    __bind_key__ = 'drive_stats'
    __tablename__ = 'set_types'

    set_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_name = db.Column(db.String(50), nullable=False, unique=True)
    two_piece_effect = db.Column(db.Text)  # 二件套效果
    four_piece_effect = db.Column(db.Text)  # 四件套效果
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<SetType {self.set_id}: {self.set_name}>'

    def to_dict(self):
        return {
            'set_id': self.set_id,
            'set_name': self.set_name,
            'two_piece_effect': self.two_piece_effect,
            'four_piece_effect': self.four_piece_effect,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }