from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import json
import os

# Secret key for JWT tokens
SECRET_KEY = "immunoai-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple file-based user storage (no database needed!)
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def get_user(email: str):
    users = load_users()
    return users.get(email)

def create_user(email: str, password: str, name: str):
    users = load_users()
    if email in users:
        return None  # User already exists
    users[email] = {
        "email": email,
        "name": name,
        "password": pwd_context.hash(password)
    }
    save_users(users)
    return users[email]

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": email, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None