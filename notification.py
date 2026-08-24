import json
import os
from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from modules.paths import data_path

def data_file():
    return data_path("notifications.json")


class NotificationManager:
    @staticmethod
    def create_file():
        os.makedirs(os.path.dirname(data_file()), exist_ok=True)
        if not os.path.exists(data_file()):
            with open(data_file(), "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

    @staticmethod
    def load_notifications():
        NotificationManager.create_file()
        try:
            with open(data_file(), "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    @staticmethod
    def save_notifications(notifications):
        NotificationManager.create_file()
        with open(data_file(), "w", encoding="utf-8") as file:
            json.dump(notifications, file, indent=4)

    @staticmethod
    def add_notification(title, message, notification_type="general"):
        notifications = NotificationManager.load_notifications()
        notifications.append({
            "title": title,
            "message": message,
            "type": notification_type,
            "time": datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"),
        })
        NotificationManager.save_notifications(notifications)
        toast(message)

    @staticmethod
    def clear_notifications():
        NotificationManager.save_notifications([])


class NotificationScreen(MDScreen):
    def on_enter(self):
        self.load_notifications()

    def go_back(self):
        self.manager.current = "home"

    def clear_all(self):
        NotificationManager.clear_notifications()
        self.load_notifications()
        toast("All notifications cleared")

    def load_notifications(self):
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        container = self.ids.notification_list
        container.clear_widgets()
        notifications = NotificationManager.load_notifications()
        if not notifications:
            container.add_widget(MDLabel(text="No notifications available.", halign="center"))
            return
        icons = {"sos": "🚨", "photo": "📷", "video": "🎥", "audio": "🎤", "location": "📍", "contacts": "👥", "general": "🔔"}
        for item in reversed(notifications):
            icon = icons.get(item.get("type", "general"), "🔔")
            card = MDCard(orientation="vertical", padding="15dp", spacing="8dp", size_hint_y=None, height="130dp", elevation=5, radius=[15])
            card.add_widget(MDLabel(text=f"{icon} {item.get('title', 'Notification')}", bold=True, font_style="H6"))
            card.add_widget(MDLabel(text=item.get("message", "")))
            card.add_widget(MDLabel(text=item.get("time", ""), halign="right", theme_text_color="Hint"))
            container.add_widget(card)
