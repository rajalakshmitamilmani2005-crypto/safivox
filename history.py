import json
import os
from datetime import datetime
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.screen import MDScreen
from modules.paths import data_path


class HistoryScreen(MDScreen):
    HISTORY_FILE = None

    def on_enter(self):
        self.HISTORY_FILE = data_path("history.json")
        self.load_history()

    def go_back(self):
        self.manager.current = "home"

    def read_history(self):
        os.makedirs(os.path.dirname(self.HISTORY_FILE), exist_ok=True)
        if not os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump([], file)
        try:
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_history(self, event):
        history = self.read_history()
        history.append({"time": datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"), "event": event})
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

    def load_history(self):
        if "history_list" not in self.ids:
            return
        self.ids.history_list.clear_widgets()
        history = list(reversed(self.read_history()))
        if not history:
            self.ids.history_list.add_widget(MDLabel(text="No History Available", halign="center"))
            return
        for item in history:
            self.ids.history_list.add_widget(TwoLineListItem(text=item.get("event", ""), secondary_text=item.get("time", "")))

    def clear_history(self):
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)
        toast("History Cleared")
        self.load_history()
