"""Safivox login screen."""
import re
from kivy.app import App
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from modules.auth import AuthStore


class LoginScreen(Screen):
    email_error = StringProperty("")
    password_error = StringProperty("")
    general_error = StringProperty("")
    password_visible = BooleanProperty(False)

    def on_pre_enter(self):
        self.email_error = ""
        self.password_error = ""
        self.general_error = ""
        self.password_visible = False
        try:
            self.ids.password_field.password = True
        except Exception:
            pass

    @staticmethod
    def is_valid_email(email):
        return re.match(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email
        ) is not None

    def login(self):
        self.email_error = ""
        self.password_error = ""
        self.general_error = ""

        email = self.ids.email_field.text.strip().lower()
        password = self.ids.password_field.text

        if not email:
            self.email_error = "Please enter your email"
            return
        if not self.is_valid_email(email):
            self.email_error = "Email is invalid"
            return
        if not password:
            self.password_error = "Please enter your password"
            return
        if len(password) < 6:
            self.password_error = "Password must contain at least 6 characters"
            return

        user = AuthStore.authenticate(email, password)
        if user is None:
            # Distinguish account existence without exposing stored hashes.
            users = AuthStore.load()
            exists = any(
                isinstance(u, dict) and str(u.get("email", "")).strip().lower() == email
                for u in users
            )
            if exists:
                self.password_error = "Invalid password"
            else:
                self.email_error = "Email is not registered"
            return

        app = App.get_running_app()
        if app:
            app.current_user = user

        try:
            home = self.manager.get_screen("home")
            home.user_name = user.get("name", "User")
            home.user_email = user.get("email", "")
        except Exception:
            pass

        toast("Login successful")
        self.manager.current = "home"

    def go_to_signup(self):
        self.manager.current = "signup"

    # Compatibility with older KV files.
    open_signup = go_to_signup

    def forgot_password(self):
        self.manager.current = "forgot_password"

    # Compatibility with older KV files.
    open_forgot_password = forgot_password

    def go_back(self):
        self.manager.current = "login"

    def continue_with_google(self):
        # Do not pretend that Google authentication succeeded. A real Google
        # OAuth/Credential Manager client ID and redirect configuration are
        # required before this can create a Google session.
        try:
            from modules.google_auth import GoogleAuth
            GoogleAuth(error_callback=lambda msg: self._google_error(msg)).sign_in()
        except Exception as error:
            self._google_error(str(error))

    def _google_error(self, message):
        self.general_error = "Google sign-in is not configured yet."
        print("Google sign-in:", message)

    def toggle_password(self):
        self.password_visible = not self.password_visible
        try:
            self.ids.password_field.password = not self.password_visible
        except Exception:
            pass
