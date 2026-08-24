from kivymd.uix.screen import MDScreen


class PrivacyScreen(MDScreen):
    def go_back(self):
        self.manager.current = "home"
