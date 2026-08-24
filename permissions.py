from kivy.utils import platform


def request_android_permissions():
    if platform != "android":
        return
    try:
        from android.permissions import request_permissions, Permission
        names = [Permission.CAMERA, Permission.RECORD_AUDIO,
                 Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION,
                 Permission.SEND_SMS]
        try:
            names.append(Permission.POST_NOTIFICATIONS)
        except AttributeError:
            pass
        request_permissions(names)
    except Exception as exc:
        print("Permission request error:", exc)
