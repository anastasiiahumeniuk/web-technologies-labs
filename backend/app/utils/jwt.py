import jwt
from datetime import datetime, timedelta
from app.core.settings import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRES_DELTA

def create_jwt(client_id: int) -> str:
    payload = {
        "client_id": client_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + JWT_EXPIRES_DELTA
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
