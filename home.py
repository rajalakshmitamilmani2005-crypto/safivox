import os

from kivy.app import App
from kivy.properties import StringProperty, ListProperty
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen


from modules.session import SessionManager


class HomeScreen(MDScreen):

    safety_status = StringProperty("SAFE")
    safety_color = ListProperty([0.08, 0.67, 0.38, 1])

    # ==================================================
    # USER DATA
    # ==================================================

    user_name = StringProperty("User")

    user_email = StringProperty(
        "Your safety companion"
    )

    user_photo = StringProperty("")

    app_logo = StringProperty(
        "assets/logo.png"
    )

    # ==================================================
    # SCREEN ENTER
    # ==================================================

    def on_enter(self):
        self.update_user_information()
        self.refresh_profile_image()

    # ==================================================
    # USER INFORMATION
    # ==================================================

    def set_user_info(
        self,
        name=None,
        email=None,
        photo=None
    ):

        if name is not None:
            self.user_name = str(name)

        if email is not None:
            self.user_email = str(email)

        if photo is not None:
            self.user_photo = str(photo)

        self.update_user_information()
        self.refresh_profile_image()

    def update_user_information(self):

        if "welcome_name" in self.ids:

            self.ids.welcome_name.text = (
                f"Hello, {self.user_name}"
            )

        if "user_email" in self.ids:

            self.ids.user_email.text = (
                self.user_email
                if self.user_email
                else "Your safety companion"
            )

    # ==================================================
    # PROFILE PHOTO
    # ==================================================

    def refresh_profile_image(self):

        if "profile_image" not in self.ids:
            return

        photo = self.user_photo

        if photo and os.path.exists(photo):

            self.ids.profile_image.source = photo

        else:

            fallback = "assets/profile.png"

            if os.path.exists(fallback):
                self.ids.profile_image.source = fallback
            else:
                # No image available.
                self.ids.profile_image.source = ""

        try:
            self.ids.profile_image.reload()
        except Exception:
            pass

    def set_profile_photo(
        self,
        image_path
    ):

        if not image_path:
            return False

        image_path = str(image_path)

        if not os.path.exists(image_path):

            print(
                "Profile image not found:",
                image_path
            )

            return False

        self.user_photo = image_path

        # Save photo path to session.
        SessionManager.update_profile(
            profile_photo=image_path
        )

        self.refresh_profile_image()

        return True

    # ==================================================
    # SOS
    # ==================================================

    def sos_pressed(self):

        if self.manager:
            self.manager.current = "sos"

    # ==================================================
    # CONTACTS
    # ==================================================

    def contacts_pressed(self):

        if self.manager:
            self.manager.current = "contacts"

    # ==================================================
    # LOCATION
    # ==================================================

    def location_pressed(self):

        if self.manager:
            self.manager.current = "location"

    # ==================================================
    # EVIDENCE
    # ==================================================

    def evidence_pressed(self):

        if self.manager:
            self.manager.current = "evidence"

    # ==================================================
    # HISTORY
    # ==================================================

    def history_pressed(self):

        if self.manager:
            self.manager.current = "history"

    # ==================================================
    # PROFILE
    # ==================================================

    def profile_pressed(self):

        if not self.manager:
            return

        try:

            if not self.manager.has_screen("profile"):
                return

            profile = self.manager.get_screen(
                "profile"
            )

            # Pass profile information to Profile screen.
            if hasattr(profile, "user_photo"):
                profile.user_photo = self.user_photo

            if hasattr(profile, "first_name"):
                profile.first_name = (
                    self.user_name.split(" ")[0]
                    if self.user_name
                    else ""
                )

            if hasattr(profile, "email"):
                profile.email = self.user_email

            self.manager.current = "profile"

        except Exception as e:

            print(
                "Profile navigation error:",
                e
            )

    # ==================================================
    # NOTIFICATIONS
    # ==================================================

    def notification_pressed(self):

        if self.manager and self.manager.has_screen(
            "notification"
        ):
            self.manager.current = "notification"

    # ==================================================
    # SETTINGS
    # ==================================================

    def settings_pressed(self):

        if self.manager and self.manager.has_screen(
            "settings"
        ):
            self.manager.current = "settings"

    # ==================================================
    # HELP
    # ==================================================

    def help_pressed(self):

        if self.manager and self.manager.has_screen(
            "help"
        ):
            self.manager.current = "help"

    # ==================================================
    # ABOUT
    # ==================================================

    def about_pressed(self):

        if self.manager and self.manager.has_screen(
            "about"
        ):
            self.manager.current = "about"

    # ==================================================
    # PRIVACY
    # ==================================================

    def privacy_pressed(self):

        if self.manager and self.manager.has_screen(
            "privacy"
        ):
            self.manager.current = "privacy"

    # ==================================================
    # DRAWER
    # ==================================================

    def open_menu(self):

        try:
            self.ids.nav_drawer.set_state("open")
        except Exception as e:
            print("Menu error:", e)

    def close_menu(self):

        try:
            self.ids.nav_drawer.set_state("close")
        except Exception:
            pass

    # ==================================================
    # LOGOUT
    # ==================================================

    def logout(self):

        success = SessionManager.logout()

        if not success:
            toast("Logout failed")
            return

        self.user_name = "User"
        self.user_email = "Your safety companion"
        self.user_photo = ""

        self.refresh_profile_image()

        toast("Logged out successfully")

        if (
            self.manager
            and self.manager.has_screen("login")
        ):
            self.manager.current = "login"

    # ==================================================
    # RATE APP
    # ==================================================

    def rate_app(self):

        toast(
            "Thank you for supporting Safivox"
        )

    # ==================================================
    # EXIT
    # ==================================================

    def exit_app(self):

        app = App.get_running_app()

        if app:
            app.stop()