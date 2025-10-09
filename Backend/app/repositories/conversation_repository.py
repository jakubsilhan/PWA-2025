from app.extensions import db
from sqlalchemy import desc
from app.models.conversation import Conversation
from app.models.user import User
from app.models.message import Message

class ConversationRepository:
    
    def get_all(self):
        """Retrieves all conversation.
        
        :returns: List[Conversation]
        """
        return db.session.execute(db.select(Conversation)).scalars().all()

    def get_by_id(self, conversation_id):
        """Retrieves a single conversation by its ID.
        
        :returns: Conversation
        """
        return db.get_or_404(Conversation, conversation_id)
    

    def create(self, chat_name, initial_user_id):
        """Creates and persists a new conversation.
        
        :returns: Conversation
        """
        initial_user = db.session.get(User, initial_user_id)
        if not initial_user:
            raise ValueError("Initial user does not exist!")
        
        new_conversation = Conversation(chat_name=chat_name)

        new_conversation.users.append(initial_user)
        
        db.session.add(new_conversation)

        db.session.commit() 
        return new_conversation

    def add_user(self, conversation_id, user_id):
        """Adds a user to a conversation.
        
        :returns: Boolean
        """
        conversation = self.get_by_id(conversation_id)
        user = db.session.get(User, user_id)

        if not user:
            raise ValueError("User does not exist!")
        
        if user not in conversation.users:
            conversation.users.append(user)
            db.session.commit()
            return True
        return False
    
    def get_users(self, conversation_id):
        """Fetches all users for conversation.
        
        :returns: List[User]
        """
        conversation = self.get_by_id(conversation_id)
        
        return conversation.users

    def delete(self, conversation_id):
        """Deletes a conversation by its ID.
        
        :returns: Boolean
        """
        conversation = self.get_by_id(conversation_id)

        db.session.delete(conversation)
        db.session.commit()

        return True
    

    # Messages
    def add_message(self, conversation_id, sender_id, content):
        """Creates a new message and persists it in a conversation with associated user.
        
        :returns: Message
        """

        conversation = self.get_by_id(conversation_id)
        sender = db.session.get(User, sender_id)

        if not sender:
            raise ValueError("User does not exist!")

        new_message = Message(
            content = content,
            sender = sender
        )

        conversation.messages.append(new_message)
        db.session.commit()
        return new_message
    
    def get_message_slice(self, conversation_id, offset, limit):
        """Fetches paginated slice of date ordered messages from a conversation.
        
        :returns: List[Message]
        """
        query = (
            db.select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(desc(Message.timestamp))
            .offset(offset)
            .limit(limit)
        )

        return db.session.execute(query).scalars().all()