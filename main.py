# ==========================================================
# SAFIVOX - MAIN
# ==========================================================

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.floatlayout import FloatLayout

from kivymd.app import MDApp


# ==========================================================
# SCREENS
# ==========================================================

from modules.splash import SplashScreen
from modules.login import LoginScreen
from modules.signup import SignupScreen
from modules.forgot_password import ForgotPasswordScreen

from modules.home import HomeScreen
from modules.contacts import ContactsScreen
from modules.location import LocationScreen
from modules.evidence import EvidenceScreen
from modules.sos import SOSScreen
from modules.history import HistoryScreen
from modules.settings import SettingsScreen
from modules.profile import ProfileScreen
from modules.about import AboutScreen
from modules.privacy import PrivacyScreen
from modules.help import HelpScreen
from modules.notification import NotificationScreen

from modules.footer import SafivoxFooter


# ==========================================================
# KV FILES
# ==========================================================

KV_FILES = [
    "kv/footer.kv",

    "kv/splash.kv",
    "kv/login.kv",
    "kv/signup.kv",
    "kv/forgot_password.kv",

    "kv/home.kv",
    "kv/contacts.kv",
    "kv/location.kv",
    "kv/evidence.kv",
    "kv/sos.kv",
    "kv/history.kv",
    "kv/settings.kv",
    "kv/profile.kv",
    "kv/about.kv",
    "kv/privacy.kv",
    "kv/help.kv",
    "kv/notification.kv",
]


# ==========================================================
# PAGES WITHOUT FOOTER
# ==========================================================

AUTH_SCREENS = {
    "splash",
    "login",
    "signup",
    "forgot_password",
}


class SafivoxApp(MDApp):

    current_user = None
    screen_manager = None
    footer = None
    root_layout = None

    # ======================================================
    # BUILD
    # ======================================================

    def build(self):

        self.title = "Safivox"

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Pink"
        self.theme_cls.primary_hue = "500"

        # --------------------------------------------------
        # APP ICON
        # --------------------------------------------------

        try:
            Window.icon = "assets/app_icon.png"
        except Exception as error:
            print(
                "Application icon error:",
                error
            )

        # --------------------------------------------------
        # LOAD KV
        # --------------------------------------------------

        for kv_file in KV_FILES:

            print(
                "Loading",
                kv_file
            )

            Builder.load_file(
                kv_file
            )

        # --------------------------------------------------
        # SCREEN MANAGER
        # --------------------------------------------------

        sm = ScreenManager(
            transition=FadeTransition(
                duration=0.18
            )
        )

        self.screen_manager = sm

        # --------------------------------------------------
        # REGISTER SCREENS
        # --------------------------------------------------

        screens = [

            SplashScreen(name="splash"),

            LoginScreen(name="login"),

            SignupScreen(name="signup"),

            ForgotPasswordScreen(
                name="forgot_password"
            ),

            HomeScreen(name="home"),

            ProfileScreen(name="profile"),

            ContactsScreen(name="contacts"),

            LocationScreen(name="location"),

            EvidenceScreen(name="evidence"),

            SOSScreen(name="sos"),

            HistoryScreen(name="history"),

            SettingsScreen(name="settings"),

            AboutScreen(name="about"),

            PrivacyScreen(name="privacy"),

            HelpScreen(name="help"),

            NotificationScreen(
                name="notification"
            ),
        ]

        for screen in screens:

            sm.add_widget(screen)

            print(
                "Registered:",
                screen.name
            )

        # ==================================================
        # SCREEN CHANGE EVENT
        # ==================================================

        sm.bind(
            current=self.on_screen_change
        )

        # ==================================================
        # ROOT LAYOUT
        # ==================================================

        root_layout = FloatLayout()

        self.root_layout = root_layout

        # --------------------------------------------------
        # Screen manager
        # --------------------------------------------------

        sm.size_hint = (
            1,
            0.91
        )

        sm.pos_hint = {
            "x": 0,
            "y": 0.09
        }

        root_layout.add_widget(
            sm
        )

        # ==================================================
        # FOOTER
        # ==================================================

        try:

            footer = SafivoxFooter()

            self.footer = footer

            footer.manager = sm

            footer.size_hint = (
                1,
                0.09
            )

            footer.pos_hint = {
                "x": 0,
                "y": 0
            }

            footer.opacity = 0
            footer.disabled = True

            root_layout.add_widget(
                footer
            )

            print(
                "Safivox footer created"
            )

        except Exception as error:

            print(
                "Footer error:",
                error
            )

            self.footer = None

        # --------------------------------------------------
        # START
        # --------------------------------------------------

        sm.current = "splash"

        return root_layout

    # ======================================================
    # SCREEN CHANGE
    # ======================================================

    def on_screen_change(
        self,
        screen_manager,
        current_name
    ):

        print(
            "Current screen:",
            current_name
        )

        if self.footer is None:
            return

        # --------------------------------------------------
        # Hide footer for authentication pages
        # --------------------------------------------------

        if current_name in AUTH_SCREENS:

            self.footer.opacity = 0
            self.footer.disabled = True

            print(
                "Footer hidden on:",
                current_name
            )

        # --------------------------------------------------
        # Show footer after login
        # --------------------------------------------------

        else:

            self.footer.opacity = 1
            self.footer.disabled = False

            print(
                "Footer visible on:",
                current_name
            )

    # ======================================================
    # ANDROID PERMISSIONS
    # ======================================================

    def on_start(self):

        try:

            from modules.permissions import (
                request_android_permissions
            )

            request_android_permissions()

        except Exception as error:

            print(
                "Android permission error:",
                error
            )


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    SafivoxApp().run()