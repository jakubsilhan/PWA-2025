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

        if not self.repository.add(email=email, username=username, hashed_password=hashed_pw):
            return False

        return True



    def login_user(self, email, password):
        user = self.repository.get_by_email(email)

        if user is None:
            raise ValueError("Email not registered!")
        

        if not check_pw(user.password, password):
            raise ValueError("Invalid password!")
        
        access_token = create_access_token(identity=str(user.id))
        # refresh_token = create_refresh_token(identity=user.id)

        # return {
        #     "access_token": access_token,
        #     "refresh_token": refresh_token
        # }

        return access_token


    def get_profiles(self, username):
        return self.repository.get_by_username(username, 5)