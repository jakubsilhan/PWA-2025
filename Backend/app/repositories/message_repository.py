from app.extensions import db
from app.models.message import Message

import datetime

class MessageRepository:
    
    def get_all(self):
        """Retrieves all messages.
        
        :returns: List[Message]
        """
        return db.session.execute(db.select(Message)).scalars().all()

    def get_by_id(self, message_id):
        """Retrieves a single message by their ID.
        
        :returns: Message
        """
        return db.get_or_404(Message, message_id)
    
    def add(self, new_message: Message):
        """Persists a new message.
        
        :returns: Message
        """
        
        db.session.add(new_message)

        db.session.commit() 
        return new_message
    
    def add(self, content, conversation_id, user_id):
        """Creates and persists a new message.
        
        :returns: Message
        """

        new_message = Message(
            content = content,
            conversation_id = conversation_id,
            user_id = user_id
        )
        
        db.session.add(new_message)

        db.session.commit() 
        return new_message

    def update_username(self, message_id, new_content):
        """Updates a user's username.
        
        :returns: Message
        """
        message = self.get_by_id(message_id)

        message.content = new_content
        message.timestamp = datetime.datetime.now(datetime.timezone.utc)
        db.session.commit()
        return message
        

    def delete(self, message_id):
        """Deletes a user by their ID.
        
        :returns: Boolean
        """
        message = self.get_by_id(message_id)

        db.session.delete(message)
        db.session.commit()

        return True