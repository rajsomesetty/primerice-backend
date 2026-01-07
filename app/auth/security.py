from passlib.context import CryptContext
from jose import jwt
from app.config import JWT_SECRET, JWT_ALGORITHM

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd.hash(password)

def verify_password(password, hash):
    return pwd.verify(password, hash)

def create_token(data):
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

