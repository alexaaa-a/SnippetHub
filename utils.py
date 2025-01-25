import secrets
import hashlib


def generate_session_token():
    """Генерация уникального токена сессии."""
    token = secrets.token_hex(32)
    return hashlib.sha256(token.encode()).hexdigest()

