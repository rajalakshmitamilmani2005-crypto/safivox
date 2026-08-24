import time
import threading

from kivy.utils import platform


class AndroidVibrator:
    """
    Safivox Android vibration controller.

    Public methods:
        vibrate()
        vibrate_pattern()
        cancel()
        is_available()
    """

    def __init__(self):

        self.vibrator = None

        self.available = False

        self._lock = threading.RLock()

        self._initialize()

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def _initialize(self):

        if platform != "android":

            print(
                "Android vibrator: unavailable on desktop."
            )

            return False

        try:

            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            Context = autoclass(
                "android.content.Context"
            )

            activity = (
                PythonActivity.mActivity
            )

            self.vibrator = (
                activity.getSystemService(
                    Context.VIBRATOR_SERVICE
                )
            )

            if self.vibrator is None:

                print(
                    "Android vibrator unavailable."
                )

                return False

            self.available = True

            print(
                "Android vibrator: initialized."
            )

            return True

        except Exception as e:

            print(
                "Vibrator initialization error:",
                e
            )

            self.vibrator = None
            self.available = False

            return False

    # ==========================================================
    # SIMPLE VIBRATION
    # ==========================================================

    def vibrate(
        self,
        duration_ms=500
    ):

        with self._lock:

            duration_ms = max(
                1,
                int(duration_ms)
            )

            if platform != "android":

                print(
                    f"[Desktop Vibration Simulation] "
                    f"{duration_ms} ms"
                )

                return False

            if not self.available:

                if not self._initialize():

                    return False

            try:

                # Android API 26+
                try:

                    from jnius import autoclass

                    BuildVersion = autoclass(
                        "android.os.Build$VERSION"
                    )

                    BuildCodes = autoclass(
                        "android.os.Build$VERSION_CODES"
                    )

                    VibrationEffect = autoclass(
                        "android.os.VibrationEffect"
                    )

                    if (
                        BuildVersion.SDK_INT
                        >=
                        BuildCodes.O
                    ):

                        effect = (
                            VibrationEffect
                            .createOneShot(
                                duration_ms,
                                VibrationEffect.DEFAULT_AMPLITUDE
                            )
                        )

                        self.vibrator.vibrate(
                            effect
                        )

                        return True

                except Exception:
                    pass

                # Older Android
                self.vibrator.vibrate(
                    duration_ms
                )

                return True

            except Exception as e:

                print(
                    "Vibration error:",
                    e
                )

                return False

    # ==========================================================
    # EMERGENCY PATTERN
    # ==========================================================

    def vibrate_pattern(
        self,
        pattern=None
    ):

        """
        Default pattern:
            pause
            vibrate
            pause
            vibrate
            pause
            long vibrate
        """

        if pattern is None:

            pattern = [
                0,
                300,
                200,
                300,
                200,
                700
            ]

        if platform != "android":

            print(
                "[Desktop Vibration Simulation]",
                pattern
            )

            return False

        if not self.available:

            if not self._initialize():

                return False

        try:

            import time

            # --------------------------------------------------
            # Android API 26+
            # --------------------------------------------------

            try:

                from jnius import autoclass

                BuildVersion = autoclass(
                    "android.os.Build$VERSION"
                )

                BuildCodes = autoclass(
                    "android.os.Build$VERSION_CODES"
                )

                VibrationEffect = autoclass(
                    "android.os.VibrationEffect"
                )

                if (
                    BuildVersion.SDK_INT
                    >=
                    BuildCodes.O
                ):

                    timings = [
                        int(x)
                        for x in pattern
                    ]

                    amplitudes = [
                        0,
                        255,
                        0,
                        255,
                        0,
                        255
                    ]

                    # Make amplitude length match timing.
                    amplitudes = (
                        amplitudes[:len(timings)]
                    )

                    effect = (
                        VibrationEffect
                        .createWaveform(
                            timings,
                            amplitudes,
                            -1
                        )
                    )

                    self.vibrator.vibrate(
                        effect
                    )

                    return True

            except Exception:
                pass

            # --------------------------------------------------
            # Older Android
            # --------------------------------------------------

            timings = [
                int(x)
                for x in pattern
            ]

            self.vibrator.vibrate(
                timings,
                -1
            )

            return True

        except Exception as e:

            print(
                "Vibration pattern error:",
                e
            )

            return False

    # ==========================================================
    # CANCEL
    # ==========================================================

    def cancel(self):

        if platform != "android":

            return True

        if not self.vibrator:

            return True

        try:

            self.vibrator.cancel()

            return True

        except Exception as e:

            print(
                "Vibration cancel error:",
                e
            )

            return False

    # ==========================================================
    # SOS VIBRATION
    # ==========================================================

    def emergency_vibration(self):

        return self.vibrate_pattern(
            [
                0,
                250,
                150,
                250,
                150,
                600
            ]
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def is_available(self):

        return (
            platform == "android"
            and
            self.available
        )

    # ==========================================================
    # RELEASE
    # ==========================================================

    def release(self):

        try:

            self.cancel()

        except Exception:
            pass

        self.vibrator = None
        self.available = False