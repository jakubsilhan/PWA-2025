from app import db
from sqlalchemy.orm import relationship
import datetime

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="messages")
