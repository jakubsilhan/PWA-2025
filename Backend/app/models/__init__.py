from app import db

conversation_participant = db.Table(
    'conversation_participant',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'), primary_key=True)
)

from .conversation import Conversation
from .message import Message
from .user import User
