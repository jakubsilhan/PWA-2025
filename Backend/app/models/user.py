from app import db
from sqlalchemy.orm import relationship
from . import conversation_participant

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    messages = relationship("Message", back_populates="sender")
    conversations = relationship("Conversation", secondary=conversation_participant, back_populates="users")