from app import db
from sqlalchemy.orm import relationship
from . import conversation_participant

class Conversation(db.Model):
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_name = db.Column(db.String, nullable=False)

    messages = relationship("Message", back_populates="conversation")
    users = relationship("User", secondary=conversation_participant, back_populates="conversations")