from kivymd.uix.screen import MDScreen
from kivymd.toast import toast


class HelpScreen(MDScreen):

    def on_enter(self):
        print("Help screen opened")

    def go_back(self):
        self.manager.current = "home"

    def show_message(self):
        toast("For more information, contact support.")