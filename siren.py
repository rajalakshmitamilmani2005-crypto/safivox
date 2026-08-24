import os

from kivy.core.audio import SoundLoader
from kivymd.toast import toast


class SirenManager:

    def __init__(self):

        self.sound = None
        self.is_playing = False

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.sound_path = os.path.join(
            base_dir,
            "assets",
            "audio",
            "siren.mp3"
        )

    def load(self):

        print(
            "Siren path:",
            self.sound_path
        )

        if not os.path.isfile(
            self.sound_path
        ):

            print(
                "Siren file not found:",
                self.sound_path
            )

            return False

        try:

            self.sound = SoundLoader.load(
                self.sound_path
            )

            if self.sound is None:

                print(
                    "Kivy failed to load siren audio"
                )

                return False

            return True

        except Exception as e:

            print(
                "Siren load error:",
                e
            )

            return False

    def start(self):

        if self.is_playing:
            return True

        if self.sound is None:

            if not self.load():

                toast(
                    "Siren audio not available"
                )

                return False

        try:

            self.sound.loop = True
            self.sound.volume = 1.0
            self.sound.play()

            self.is_playing = True

            print(
                "Siren started"
            )

            return True

        except Exception as e:

            print(
                "Siren start error:",
                e
            )

            return False

    def stop(self):

        if self.sound is not None:

            try:
                self.sound.stop()
            except Exception:
                pass

        self.is_playing = False

        print(
            "Siren stopped"
        )

    def toggle(self):

        if self.is_playing:

            self.stop()
            return False

        return self.start()

    def release(self):

        try:

            if self.sound is not None:

                self.sound.stop()
                self.sound.unload()

        except Exception:
            pass

        self.sound = None
        self.is_playing = False