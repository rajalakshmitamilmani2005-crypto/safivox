"""Safivox authentication storage.

One canonical format is used for all account operations:
    {id, name, email, password_hash, login_type}

Older Safivox files that contain a SHA-256 value in ``password`` are
accepted and migrated to ``password_hash`` automatically.
"""
import hashlib
import json
import os
from modules.paths import data_path


class AuthStore:
    @classmethod
    def file(cls):
        return data_path("users.json")

    @classmethod
    def _ensure(cls):
        os.makedirs(os.path.dirname(cls.file()), exist_ok=True)
        if not os.path.exists(cls.file()):
            with open(cls.file(), "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    @classmethod
    def load(cls):
        cls._ensure()
        try:
            with open(cls.file(), "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    @classmethod
    def save(cls, users):
        cls._ensure()
        temp = cls.file() + ".tmp"
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        os.replace(temp, cls.file())

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def _get_hash(cls, user):
        # New format first.
        value = str(user.get("password_hash", "")).strip()
        if value:
            return value
        # Backward compatibility with the older project format.
        return str(user.get("password", "")).strip()

    @classmethod
    def authenticate(cls, email, password):
        email = email.strip().lower()
        entered_hash = cls.hash_password(password)
        users = cls.load()
        changed = False

        for user in users:
            if not isinstance(user, dict):
                continue
            if str(user.get("email", "")).strip().lower() != email:
                continue

            stored_hash = cls._get_hash(user)
            if stored_hash and stored_hash == entered_hash:
                # Migrate old ``password`` records to the canonical field.
                if not user.get("password_hash"):
                    user["password_hash"] = stored_hash
                    user.pop("password", None)
                    changed = True
                if changed:
                    try:
                        cls.save(users)
                    except OSError:
                        pass
                return user
            return None
        return None

    @classmethod
    def register(cls, name, email, password):
        users = cls.load()
        email = email.strip().lower()
        if any(
            str(u.get("email", "")).strip().lower() == email
            for u in users if isinstance(u, dict)
        ):
            return False, "An account with this email already exists."

        users.append({
            "id": max([int(u.get("id", 0)) for u in users if isinstance(u, dict)] + [0]) + 1,
            "name": name.strip(),
            "email": email,
            "password_hash": cls.hash_password(password),
            "login_type": "email",
        })
        cls.save(users)
        return True, "Account created successfully."

    @classmethod
    def reset_password(cls, email, new_password):
        email = email.strip().lower()
        users = cls.load()
        for user in users:
            if isinstance(user, dict) and str(user.get("email", "")).strip().lower() == email:
                user["password_hash"] = cls.hash_password(new_password)
                user.pop("password", None)
                user["login_type"] = "email"
                cls.save(users)
                return True
        return False
