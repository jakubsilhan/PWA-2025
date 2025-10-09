import bcrypt

def hash_password(password: str) -> str:
    """Hashes the password"""
    bytes_pw = password.encode("utf-8")

    salt = bcrypt.gensalt()
    h = bcrypt.hashpw(bytes_pw, salt)

    return h.decode("utf-8")

def check_pw(hashed: str, password: str) -> bool:
    """Checks password against a hashed one"""
    bytes_pw = password.encode("utf-8")
    bytes_hashed = hashed.encode("utf-8")

    return bcrypt.checkpw(bytes_pw, bytes_hashed)