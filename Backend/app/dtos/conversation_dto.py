from dataclasses import dataclass
from app.models.conversation import Conversation

@dataclass
class ConversationDTO:
    id: int
    chat_name: str
    last_message: str
    last_message_username: str
    last_message_time: str
    can_access: bool

    @classmethod
    def from_conversation(cls, conversation: Conversation):
        """Create a ConversationDTO from a Conversation ORM instance"""
        last_message = ""
        last_message_username = ""
        last_message_time = ""
        can_access = False
        
        return cls(
            id=conversation.id,
            chat_name=conversation.chat_name,
            last_message=last_message,
            last_message_username=last_message_username,
            last_message_time=last_message_time,
            can_access = can_access
        )