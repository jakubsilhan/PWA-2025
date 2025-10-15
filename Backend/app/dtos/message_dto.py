from dataclasses import dataclass
from app.models.message import Message

@dataclass
class MessageDTO:
    id: int
    content: str
    timestamp: str
    conversation_id: int
    sender_name: str

    @classmethod
    def from_message(cls, message: Message):
        """Create a MessageDTO from a Message ORM instance"""
        return cls(id=message.id, content=message.content, timestamp=message.timestamp.isoformat(), conversation_id=message.conversation_id, sender_name=message.sender.username)