import json
import os

from kivy.app import App


class SessionManager:

    FILE_NAME = "session.json"

    @classmethod
    def get_data_directory(cls):
        app = App.get_running_app()
        if app is not None:
            directory = app.user_data_dir
        else:
            directory = os.path.join(os.getcwd(), "data")
        os.makedirs(directory, exist_ok=True)
        return directory

    @classmethod
    def get_profile_directory(cls):
        directory = os.path.join(cls.get_data_directory(), "profile")
        os.makedirs(directory, exist_ok=True)
        return directory

    @classmethod
    def get_file_path(cls):
        return os.path.join(cls.get_data_directory(), cls.FILE_NAME)

    @classmethod
    def get_profile_photo_path(cls):
        return os.path.join(cls.get_profile_directory(), "profile_photo.jpg")

    @classmethod
    def default_data(cls):
        return {
            "logged_in": False,
            "name": "",
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone": "",
            "blood_group": "",
            "gender": "",
            "address": "",
            "profile_photo": "",
        }

    @classmethod
    def load(cls):
        try:
            path = cls.get_file_path()
            if not os.path.exists(path):
                return cls.default_data()
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                return cls.default_data()
            result = cls.default_data()
            result.update(data)
            # Backward compatibility: derive first/last names from legacy name.
            if not result.get("name"):
                result["name"] = " ".join(
                    p for p in [result.get("first_name", ""), result.get("last_name", "")]
                    if p
                ).strip()
            if not result.get("first_name") and result.get("name"):
                parts = result["name"].split()
                result["first_name"] = parts[0]
                result["last_name"] = " ".join(parts[1:])
            return result
        except Exception as e:
            print("Session load error:", e)
            return cls.default_data()

    @classmethod
    def save(
        cls,
        logged_in=False,
        name="",
        first_name="",
        last_name="",
        email="",
        phone="",
        blood_group="",
        gender="",
        address="",
        profile_photo="",
    ):
        if not name:
            name = " ".join(
                p for p in [first_name, last_name] if p
            ).strip()
        if not first_name and name:
            parts = str(name).split()
            first_name = parts[0]
            last_name = " ".join(parts[1:])

        data = {
            "logged_in": bool(logged_in),
            "name": str(name or ""),
            "first_name": str(first_name or ""),
            "last_name": str(last_name or ""),
            "email": str(email or ""),
            "phone": str(phone or ""),
            "blood_group": str(blood_group or ""),
            "gender": str(gender or ""),
            "address": str(address or ""),
            "profile_photo": str(profile_photo or ""),
        }

        try:
            with open(cls.get_file_path(), "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print("Session save error:", e)
            return False

    @classmethod
    def update_profile(
        cls,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        blood_group=None,
        gender=None,
        address=None,
        profile_photo=None,
        name=None,
    ):
        data = cls.load()
        if first_name is not None:
            data["first_name"] = str(first_name)
        if last_name is not None:
            data["last_name"] = str(last_name)
        if name is not None:
            data["name"] = str(name)
        elif first_name is not None or last_name is not None:
            data["name"] = " ".join(
                p for p in [data.get("first_name", ""), data.get("last_name", "")] if p
            ).strip()
        if email is not None:
            data["email"] = str(email)
        if phone is not None:
            data["phone"] = str(phone)
        if blood_group is not None:
            data["blood_group"] = str(blood_group)
        if gender is not None:
            data["gender"] = str(gender)
        if address is not None:
            data["address"] = str(address)
        if profile_photo is not None:
            data["profile_photo"] = str(profile_photo)
        try:
            with open(cls.get_file_path(), "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print("Profile update error:", e)
            return False

    @classmethod
    def is_logged_in(cls):
        return bool(cls.load().get("logged_in", False))

    @classmethod
    def logout(cls):
        data = cls.load()
        data["logged_in"] = False
        try:
            with open(cls.get_file_path(), "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print("Logout error:", e)
            return False
