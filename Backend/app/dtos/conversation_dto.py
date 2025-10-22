from dataclasses import dataclass
from app.models.conversation import Conversation

@dataclass
class ConversationDTO:
    id: int
    chat_name: str
    last_message: str
    last_message_username: str
    last_message_time: str

    @classmethod
    def from_conversation(cls, conversation: Conversation):
        """Create a ConversationDTO from a Conversation ORM instance"""
        return cls(id=conversation.id, chat_name=conversation.chat_name)