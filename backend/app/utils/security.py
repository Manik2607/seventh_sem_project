import hashlib

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the plain text password matches the stored hash.
    """
    return hash_password(plain_password) == hashed_password
