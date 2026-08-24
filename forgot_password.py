# ==========================================================
# SAFIVOX - FORGOT PASSWORD
# ==========================================================

import os
import json
import re
import hashlib

from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen

from kivymd.toast import toast
from modules.auth import AuthStore


class ForgotPasswordScreen(Screen):

    # ======================================================
    # UI PROPERTIES
    # ======================================================

    email_error = StringProperty("")
    password_error = StringProperty("")
    confirm_error = StringProperty("")

    # This property is used by forgot_password.kv
    message = StringProperty("")

    # Optional general error
    general_error = StringProperty("")

    password_visible = BooleanProperty(False)
    confirm_password_visible = BooleanProperty(False)

    # ======================================================
    # DATA PATH
    # ======================================================

    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    DATA_DIR = os.path.join(
        BASE_DIR,
        "data"
    )

    USERS_FILE = os.path.join(
        DATA_DIR,
        "users.json"
    )

    # ======================================================
    # SCREEN ENTER
    # ======================================================

    def on_pre_enter(self):

        self.clear_messages()

    # ======================================================
    # CLEAR MESSAGES
    # ======================================================

    def clear_messages(self):

        self.email_error = ""
        self.password_error = ""
        self.confirm_error = ""
        self.message = ""
        self.general_error = ""

        try:
            self.ids.email_field.text = ""
            self.ids.password_field.text = ""
            self.ids.confirm_password_field.text = ""
        except Exception:
            pass

    # ======================================================
    # EMAIL VALIDATION
    # ======================================================

    def is_valid_email(self, email):

        pattern = (
            r"^[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\."
            r"[A-Za-z]{2,}$"
        )

        return bool(
            re.match(
                pattern,
                email
            )
        )

    # ======================================================
    # HASH PASSWORD
    # ======================================================

    def hash_password(self, password):

        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

    # ======================================================
    # LOAD USERS
    # ======================================================

    def load_users(self):

        try:

            if not os.path.exists(
                self.USERS_FILE
            ):

                return []

            with open(
                self.USERS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if isinstance(
                data,
                list
            ):

                return data

        except Exception as error:

            print(
                "Load users error:",
                error
            )

        return []

    # ======================================================
    # SAVE USERS
    # ======================================================

    def save_users(self, users):

        try:

            os.makedirs(
                self.DATA_DIR,
                exist_ok=True
            )

            with open(
                self.USERS_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    users,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except Exception as error:

            print(
                "Save users error:",
                error
            )

            return False

    # ======================================================
    # RESET PASSWORD
    # ======================================================

    def reset_password(self):
        self.email_error = ""
        self.password_error = ""
        self.confirm_error = ""
        self.message = ""
        self.general_error = ""

        try:
            email = self.ids.email_field.text.strip().lower()
            new_password = self.ids.password_field.text
            confirm_password = self.ids.confirm_password_field.text
        except Exception as error:
            print("Forgot password field error:", error)
            self.general_error = "Unable to read fields"
            return

        if not email:
            self.email_error = "Please enter your email"; return
        if not self.is_valid_email(email):
            self.email_error = "Email is invalid"; return
        if not new_password:
            self.password_error = "Please enter a new password"; return
        if len(new_password) < 6:
            self.password_error = "Password must contain at least 6 characters"; return
        if not confirm_password:
            self.confirm_error = "Please confirm your new password"; return
        if new_password != confirm_password:
            self.confirm_error = "Passwords do not match"; return

        try:
            if not AuthStore.reset_password(email, new_password):
                self.email_error = "Email is not registered"
                return
        except Exception as error:
            print("Password reset error:", error)
            self.general_error = "Unable to reset password"
            return

        self.message = "Password reset successfully. Please login."
        toast("Password reset successfully")

        try:
            self.ids.email_field.text = ""
            self.ids.password_field.text = ""
            self.ids.confirm_password_field.text = ""
        except Exception:
            pass

    def go_back(self):
        self.manager.current = "login"

    def toggle_password(self):
        self.password_visible = not self.password_visible
        try:
            self.ids.password_field.password = not self.password_visible
        except Exception:
            pass

    def toggle_confirm_password(self):
        self.confirm_password_visible = not self.confirm_password_visible
        try:
            self.ids.confirm_password_field.password = not self.confirm_password_visible
        except Exception:
            pass
