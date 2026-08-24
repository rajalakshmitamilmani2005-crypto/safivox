import os
from kivy.app import App


def app_data_dir():
    app = App.get_running_app()
    if app is not None:
        path = app.user_data_dir
        os.makedirs(path, exist_ok=True)
        return path
    return os.path.abspath("data")


def data_path(*parts):
    path = os.path.join(app_data_dir(), "data", *parts)
    if App.get_running_app() is not None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def evidence_path(kind, *parts):
    path = os.path.join(app_data_dir(), "evidence", kind, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def evidence_dir(kind):
    path = os.path.join(app_data_dir(), "evidence", kind)
    os.makedirs(path, exist_ok=True)
    return path


def profile_path(*parts):
    path = os.path.join(app_data_dir(), "profile", *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def asset_path(relative):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative)
