from kivy.properties import ListProperty
from kivymd.uix.boxlayout import MDBoxLayout


class SafivoxFooter(MDBoxLayout):

    hidden_screens = ListProperty([
        "splash",
        "login",
        "signup"
    ])

    def is_hidden(self):
        """Return True when footer should be hidden."""

        try:
            if self.manager is None:
                return True

            return self.manager.current in self.hidden_screens

        except Exception:
            return False

    def go_to(self, screen_name):
        """Navigate to selected footer screen."""

        try:
            if self.manager is None:
                return

            if self.manager.has_screen(screen_name):
                self.manager.current = screen_name
            else:
                print(
                    f"[FOOTER] Screen not found: {screen_name}"
                )

        except Exception as e:
            print(
                f"[FOOTER] Navigation error: {e}"
            )