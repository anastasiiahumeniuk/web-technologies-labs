import secrets

def generate_email_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)
