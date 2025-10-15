from dataclasses import dataclass
from app.models.conversation import Conversation

@dataclass
class ConversationDTO:
    id: int
    chat_name: str

    @classmethod
    def from_conversation(cls, conversation: Conversation):
        """Create a ConversationDTO from a Conversation ORM instance"""
        return cls(id=conversation.id, chat_name=conversation.chat_name)