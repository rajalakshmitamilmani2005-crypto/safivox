from kivy.app import App
from kivy.clock import Clock
from modules.siren import SirenManager


class TestSirenApp(App):

    def build(self):

        self.siren = SirenManager()

        Clock.schedule_once(
            self.start_test,
            1
        )

        return None

    def start_test(self, *_):

        print("Testing siren...")

        success = self.siren.start()

        print(
            "Siren started:",
            success
        )

        Clock.schedule_once(
            self.stop_test,
            5
        )

    def stop_test(self, *_):

        self.siren.stop()

        print(
            "Siren test finished"
        )

        self.stop()


if __name__ == "__main__":
    TestSirenApp().run()