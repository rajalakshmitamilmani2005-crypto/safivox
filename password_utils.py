# modules/password_utils.py

import hashlib


def hash_password(password):
    """Convert normal password into SHA-256 hash."""
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def verify_password(password, stored_password):
    """
    Check normal entered password against
    the stored password hash.
    """

    return hash_password(password) == stored_password