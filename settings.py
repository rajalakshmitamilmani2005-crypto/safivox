import json
import os
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivy.app import App
from modules.paths import data_path


class SettingsScreen(MDScreen):
    SETTINGS_FILE = None

    def on_enter(self):
        self.SETTINGS_FILE = data_path("settings.json")
        self.load_settings()

    def go_back(self):
        self.manager.current = "home"

    def default_settings(self):
        return {
            "dark_mode": True,
            "countdown": 5,
            "auto_photo": True,
            "auto_video": True,
            "auto_audio": True,
            "vibration": True,
            "siren": True,
            "location": True,
            "voice": False,
            "shake": False,
        }

    def load_settings(self):
        os.makedirs(os.path.dirname(self.SETTINGS_FILE), exist_ok=True)
        if not os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(self.default_settings(), file, indent=4)
        try:
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as file:
                settings = {**self.default_settings(), **json.load(file)}
        except Exception:
            settings = self.default_settings()
        for key in ("dark_mode", "auto_photo", "auto_video", "auto_audio", "vibration", "siren", "location", "voice", "shake"):
            self.ids[key].active = bool(settings[key])
        self.ids.countdown.text = str(settings["countdown"])
        app = App.get_running_app()
        if app:
            app.theme_cls.theme_style = "Dark" if settings["dark_mode"] else "Light"

    def save_settings(self):
        try:
            countdown = max(1, int(self.ids.countdown.text))
        except (ValueError, TypeError):
            countdown = 5
        settings = {
            "dark_mode": self.ids.dark_mode.active,
            "countdown": countdown,
            "auto_photo": self.ids.auto_photo.active,
            "auto_video": self.ids.auto_video.active,
            "auto_audio": self.ids.auto_audio.active,
            "vibration": self.ids.vibration.active,
            "siren": self.ids.siren.active,
            "location": self.ids.location.active,
            "voice": self.ids.voice.active,
            "shake": self.ids.shake.active,
        }
        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4)
        App.get_running_app().theme_cls.theme_style = "Dark" if settings["dark_mode"] else "Light"
        toast("Settings Saved")

    def reset_settings(self):
        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(self.default_settings(), file, indent=4)
        self.load_settings()
        toast("Settings Reset Successfully")
