import os
import time
import hmac
import base64
import secrets
import hashlib
from typing import Optional

import jwt

SECRET_KEY = os.getenv('SECRET_KEY', 'cambia_esta_clave_secreta_para_prod')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv('ACCESS_TOKEN_EXPIRE_SECONDS', '3600'))
PBKDF2_ITERATIONS = int(os.getenv('PBKDF2_ITERATIONS', '150000'))


def hash_password(password: str) -> str:
    """Genera un hash PBKDF2 en formato: pbkdf2$iteraciones$base64salt$base64hash"""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2${PBKDF2_ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        parts = stored.split('$')
        if parts[0] != 'pbkdf2':
            return False
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2])
        hash_expected = base64.b64decode(parts[3])
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return hmac.compare_digest(dk, hash_expected)
    except Exception:
        return False


def create_access_token(data: dict, expires_in: Optional[int] = None) -> str:
    to_encode = data.copy()
    now = int(time.time())
    expire = now + (expires_in if expires_in is not None else ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode.update({'exp': expire, 'iat': now})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # PyJWT returns str
    return token


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise
    except Exception:
        raise
