from flask_jwt_extended import create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository
from app.utils.hashing import hash_password, check_pw

class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def register_user(self, username, email, password) -> bool:
        """Registers a user
        
        :returns: Boolean
        """
        if self.repository.get_by_email(email) is not None:
            raise ValueError("Email already registered!")
        
        hashed_pw = hash_password(password)

        if not self.repository.create(email=email, username=username, hashed_password=hashed_pw):
            return False

        return True


    def login_user(self, email, password):
        """Logs user in and creates an access token
        
        :returns: str
        """
        user = self.repository.get_by_email(email)

        if user is None:
            raise ValueError("Email not registered!")
        

        if not check_pw(user.password, password):
            raise ValueError("Invalid password!")
        
        access_token = create_access_token(identity=str(user.id))
        return access_token, user


    def get_profiles(self, username):
        """Retrieves 5 profiles contain username
        
        :returns: List[User]
        """
        return self.repository.get_by_username(username, 5)
    
    def get_user(self, user_id):
        """Retrieves user by user_id
        
        :returns: User
        """
        return self.repository.get_by_id(user_id)