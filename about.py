from kivymd.uix.screen import MDScreen


class AboutScreen(MDScreen):

    def go_back(self):
        self.manager.current = "home"
