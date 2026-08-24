from kivy.clock import Clock
from kivymd.uix.screen import MDScreen

from modules.session import SessionManager


class SplashScreen(MDScreen):

    def on_enter(self):
        Clock.schedule_once(
            self.check_session,
            2
        )

    def check_session(self, *_args):

        if not self.manager:
            return

        session = SessionManager.load()

        if session.get(
            "logged_in",
            False
        ):
            self.load_saved_user()
            self.manager.current = "home"

        else:
            self.manager.current = "login"

    def load_saved_user(self):

        session = SessionManager.load()

        if not self.manager.has_screen(
            "home"
        ):
            return

        home = self.manager.get_screen(
            "home"
        )

        home.set_user_info(
            name=session.get(
                "name",
                "User"
            ),
            email=session.get(
                "email",
                ""
            ),
            photo=session.get(
                "profile_photo",
                ""
            )
        )