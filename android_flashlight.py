import threading

from kivy.utils import platform


class AndroidFlashlight:
    """
    Safivox Android flashlight controller.

    Public methods used by sos.py:
        turn_on()
        turn_off()
        toggle()
        status()
        release()
    """

    def __init__(self):

        self.is_on = False
        self.available = False

        self.activity = None
        self.camera_manager = None
        self.camera_id = None

        self._lock = threading.RLock()

        if platform == "android":
            self._initialize_android()
        else:
            print(
                "Flashlight: Android torch unavailable on desktop."
            )

    # ==========================================================
    # ANDROID INITIALIZATION
    # ==========================================================

    def _initialize_android(self):

        try:
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            Context = autoclass(
                "android.content.Context"
            )

            self.activity = (
                PythonActivity.mActivity
            )

            self.camera_manager = (
                self.activity.getSystemService(
                    Context.CAMERA_SERVICE
                )
            )

            if self.camera_manager is None:
                print(
                    "Flashlight: CameraManager unavailable."
                )
                return False

            self.camera_id = (
                self._find_flash_camera()
            )

            if self.camera_id is None:
                print(
                    "Flashlight: no camera with torch found."
                )
                return False

            self.available = True

            print(
                "Flashlight: Android torch initialized."
            )

            return True

        except Exception as e:

            print(
                "Flashlight initialization error:",
                e
            )

            self.available = False

            return False

    # ==========================================================
    # FIND CAMERA WITH FLASH
    # ==========================================================

    def _find_flash_camera(self):

        try:
            from jnius import autoclass

            CameraCharacteristics = autoclass(
                "android.hardware.camera2.CameraCharacteristics"
            )

            flash_key = (
                CameraCharacteristics.FLASH_INFO_AVAILABLE
            )

            camera_ids = (
                self.camera_manager.getCameraIdList()
            )

            for camera_id in camera_ids:

                try:
                    characteristics = (
                        self.camera_manager
                        .getCameraCharacteristics(
                            camera_id
                        )
                    )

                    flash_available = (
                        characteristics.get(
                            flash_key
                        )
                    )

                    if bool(flash_available):
                        return str(camera_id)

                except Exception:
                    continue

        except Exception as e:

            print(
                "Flash camera detection error:",
                e
            )

        return None

    # ==========================================================
    # TURN ON
    # ==========================================================

    def turn_on(self):

        with self._lock:

            if self.is_on:
                return True

            if platform != "android":

                print(
                    "Flashlight ON requested on desktop."
                )

                return False

            if not self.available:

                if not self._initialize_android():
                    return False

            try:

                self.camera_manager.setTorchMode(
                    self.camera_id,
                    True
                )

                self.is_on = True

                print(
                    "Flashlight ON"
                )

                return True

            except Exception as e:

                print(
                    "Flashlight ON error:",
                    e
                )

                self.is_on = False

                return False

    # ==========================================================
    # TURN OFF
    # ==========================================================

    def turn_off(self):

        with self._lock:

            if not self.is_on:
                return True

            if platform != "android":

                self.is_on = False
                return True

            if (
                not self.available
                or not self.camera_manager
                or self.camera_id is None
            ):

                self.is_on = False
                return False

            try:

                self.camera_manager.setTorchMode(
                    self.camera_id,
                    False
                )

                self.is_on = False

                print(
                    "Flashlight OFF"
                )

                return True

            except Exception as e:

                print(
                    "Flashlight OFF error:",
                    e
                )

                self.is_on = False

                return False

    # ==========================================================
    # TOGGLE
    # ==========================================================

    def toggle(self):

        if self.is_on:
            return self.turn_off()

        return self.turn_on()

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self):
        return self.is_on

    # ==========================================================
    # RELEASE
    # ==========================================================

    def release(self):

        try:
            self.turn_off()
        except Exception:
            pass

        self.activity = None
        self.camera_manager = None
        self.camera_id = None
        self.available = False
        self.is_on = False