from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    print(f"[DEBUG] password length before trim: {len(password)}, value: {password}")
    trimmed_password = password[:72]
    return pwd_context.hash(trimmed_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    trimmed_password = plain_password[:72]
    return pwd_context.verify(trimmed_password, hashed_password)
