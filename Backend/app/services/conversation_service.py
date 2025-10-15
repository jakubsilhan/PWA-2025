from app.repositories.conversation_repository import ConversationRepository

class ConversationService:
    def __init__(self):
        self.repository = ConversationRepository()

    def get_conversations(self, user_id):
        """Retrieves all user conversations
        
        :returns: List[Conversation]
        """
        return self.repository.get_by_user_id(user_id)
    
    def is_user_in_conversation(self, user_id, conversation_id):
        """Checks if a user is part of conversation
        
        :returns: bool
        """
        conversation = self.repository.get_by_id(conversation_id)

        return any(user.id == user_id for user in conversation.users)

    def add_message(self, conversation_id, user_id, message):
        """Add a message to conversation
        
        :returns: Message
        """
        return self.repository.add_message(conversation_id, user_id, message)

    def get_messages(self, conversation_id, limit, offset):
        """Retrieves conversation message in a range
        
        :returns: List[Message]
        """
        return self.repository.get_message_slice(conversation_id, limit, offset)

    def add_user_to_conversation(self, conversation_id, new_user_id):
        """Adds a user to conversation
        
        :returns: Conversation
        """
        conversation = self.repository.add_user(conversation_id, new_user_id)

        if not conversation:
            raise ValueError("Conversation joining failed!")
        
        return conversation

    def create_conversation(self, chat_name, participant_ids: list):
        """Creates a conversation with specified users
        
        :returns: Conversation
        """
        creator_id = participant_ids[0]
        conversation = self.repository.create(chat_name, creator_id)
        for id in participant_ids[1:]:
            self.repository.add_user(conversation.id, id)
        
        return conversation