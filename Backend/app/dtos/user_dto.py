from dataclasses import dataclass
from app.models.user import User

@dataclass
class UserDTO:
    id: int
    username: str
    email: str

    @classmethod
    def from_user(cls, user: User):
        """Create a UserDTO from a User ORM instance"""
        return cls(id=user.id, username=user.username, email=user.email)