from app.extensions import db
from app.models.user import User
from sqlalchemy import select

class UserRepository:
    
    def get_all(self):
        """Retrieves all users.
        
        :returns: List[User]
        """
        return db.session.execute(db.select(User)).scalars().all()

    def get_by_id(self, user_id):
        """Retrieves a single user by their ID.
        
        :returns: User
        """
        return db.get_or_404(User, user_id)
    
    def get_by_email(self, email) -> User | None:
        """Retrieves a single user by their email
        
        :returns: User
        """
        return db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()


    def get_by_username(self, username, limit=5):
        """Retrieves users by their username.
        
        :returns: List[User]
        """
        query = (
            db.select(User)
            .where(User.username.like(f"%{username}%"))
            .limit(limit)
        )

        return db.session.execute(query).scalars().all()
    
    def add(self, new_user: User):
        """Persists a new user.
        
        :returns: User
        """
        
        db.session.add(new_user)

        db.session.commit() 
        return new_user

    def add(self, email, username, hashed_password):
        """Creates and persists a new user.
        
        :returns: User
        """
        new_user = User(
            email=email, 
            username=username, 
            password=hashed_password
        )
        
        db.session.add(new_user)

        db.session.commit() 
        return new_user

    def update_username(self, user_id, new_username):
        """Updates a user's username.
        
        :returns: User
        """
        user = self.get_by_id(user_id)
        
        user.username = new_username
        db.session.commit()

        return user

    def delete(self, user_id):
        """Deletes a user by their ID.
        
        :returns: Boolean
        """
        user = self.get_by_id(user_id)

        db.session.delete(user)
        db.session.commit()

        return True