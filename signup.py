"""Safivox account creation screen."""
import re
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from modules.auth import AuthStore


class SignupScreen(Screen):
    name_error = StringProperty("")
    email_error = StringProperty("")
    password_error = StringProperty("")
    confirm_error = StringProperty("")
    general_error = StringProperty("")
    password_visible = BooleanProperty(False)
    confirm_visible = BooleanProperty(False)

    def on_pre_enter(self):
        self.clear_errors()
        self.password_visible = False
        self.confirm_visible = False
        try:
            self.ids.password_field.password = True
            self.ids.confirm_password_field.password = True
        except Exception:
            pass

    def clear_errors(self):
        self.name_error = ""
        self.email_error = ""
        self.password_error = ""
        self.confirm_error = ""
        self.general_error = ""

    @staticmethod
    def is_valid_email(email):
        return re.match(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email
        ) is not None

    def create_account(self):
        self.clear_errors()
        try:
            name = self.ids.name_field.text.strip()
            email = self.ids.email_field.text.strip().lower()
            password = self.ids.password_field.text
            confirm = self.ids.confirm_password_field.text
        except Exception as error:
            self.general_error = "Unable to read signup fields"
            print("Signup field error:", error)
            return

        if not name:
            self.name_error = "Please enter your name"; return
        if not email:
            self.email_error = "Please enter your email"; return
        if not self.is_valid_email(email):
            self.email_error = "Email is invalid"; return
        if not password:
            self.password_error = "Please enter a password"; return
        if len(password) < 6:
            self.password_error = "Password must contain at least 6 characters"; return
        if not confirm:
            self.confirm_error = "Please confirm your password"; return
        if password != confirm:
            self.confirm_error = "Passwords do not match"; return

        try:
            ok, message = AuthStore.register(name, email, password)
        except Exception as error:
            print("Account creation error:", error)
            self.general_error = "Unable to create account"
            return

        toast(message)
        if ok:
            self.ids.password_field.text = ""
            self.ids.confirm_password_field.text = ""
            self.manager.current = "login"

    # Compatibility with older KV files.
    signup = create_account

    def open_login(self):
        self.manager.current = "login"

    def toggle_password(self):
        self.password_visible = not self.password_visible
        try:
            self.ids.password_field.password = not self.password_visible
        except Exception:
            pass

    def toggle_confirm_password(self):
        self.confirm_visible = not self.confirm_visible
        try:
            self.ids.confirm_password_field.password = not self.confirm_visible
        except Exception:
            pass
