from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.sessions import get_db
from app.models.client import Client
from app.models.client_session import ClientSession
from app.utils.jwt import decode_jwt
from datetime import datetime

security = HTTPBearer()  # зчитує Authorization: Bearer <token>

def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Client:
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        client_id = payload.get("client_id")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    # Перевіряємо, чи є токен у client_session
    session = db.query(ClientSession).filter_by(session_token=token).first()
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Client not found")

    return client
