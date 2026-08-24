import math
import time
import threading

from kivy.clock import Clock
from kivy.utils import platform


class ShakeDetection:
    """
    Safivox Android accelerometer / shake detector.

    Compatible with:

        ShakeDetection(
            callback=self.start_sos
        )
    """

    def __init__(
        self,
        callback=None,
        threshold=15.0,
        cooldown=8.0,
        required_hits=2
    ):

        self.callback = callback

        self.threshold = float(
            threshold
        )

        self.cooldown = float(
            cooldown
        )

        self.required_hits = int(
            required_hits
        )

        self.running = False
        self.available = False

        self.activity = None
        self.sensor_manager = None
        self.sensor = None
        self.sensor_listener = None

        self.last_trigger = 0.0
        self.strong_hits = 0

        self._lock = threading.RLock()

        if platform == "android":

            self._initialize_android()

        else:

            print(
                "Shake detection: Android accelerometer "
                "unavailable on desktop."
            )

    # ==========================================================
    # INITIALIZE ANDROID
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

            Sensor = autoclass(
                "android.hardware.Sensor"
            )

            self.activity = (
                PythonActivity.mActivity
            )

            self.sensor_manager = (
                self.activity.getSystemService(
                    Context.SENSOR_SERVICE
                )
            )

            if self.sensor_manager is None:

                print(
                    "Shake detection: SensorManager unavailable."
                )

                return False

            self.sensor = (
                self.sensor_manager.getDefaultSensor(
                    Sensor.TYPE_ACCELEROMETER
                )
            )

            if self.sensor is None:

                print(
                    "Shake detection: accelerometer not found."
                )

                return False

            self.available = True

            print(
                "Shake detection: Android accelerometer ready."
            )

            return True

        except Exception as e:

            print(
                "Shake initialization error:",
                e
            )

            self.available = False

            return False

    # ==========================================================
    # START
    # ==========================================================

    def start(self):

        if self.running:
            return True

        if platform != "android":

            print(
                "Shake detection start requested on desktop."
            )

            return False

        if not self.available:

            if not self._initialize_android():

                return False

        try:

            from jnius import (
                PythonJavaClass,
                java_method
            )

            owner = self

            class Listener(
                PythonJavaClass
            ):

                __javainterfaces__ = [
                    "android/hardware/SensorEventListener"
                ]

                @java_method(
                    "(Landroid/hardware/SensorEvent;)V"
                )
                def onSensorChanged(
                    self,
                    event
                ):

                    try:

                        values = event.values

                        if values is None:
                            return

                        x = float(
                            values[0]
                        )

                        y = float(
                            values[1]
                        )

                        z = float(
                            values[2]
                        )

                        owner.process_acceleration(
                            x,
                            y,
                            z
                        )

                    except Exception as e:

                        print(
                            "Sensor callback error:",
                            e
                        )

                @java_method(
                    "(Landroid/hardware/Sensor;I)V"
                )
                def onAccuracyChanged(
                    self,
                    sensor,
                    accuracy
                ):

                    pass

            self.sensor_listener = (
                Listener()
            )

            Sensor = autoclass(
                "android.hardware.Sensor"
            )

            self.sensor_manager.registerListener(
                self.sensor_listener,
                self.sensor,
                Sensor.SENSOR_DELAY_NORMAL
            )

            self.strong_hits = 0
            self.running = True

            print(
                "Shake detection: STARTED"
            )

            return True

        except Exception as e:

            print(
                "Shake start error:",
                e
            )

            self.sensor_listener = None
            self.running = False

            return False

    # ==========================================================
    # PROCESS SENSOR
    # ==========================================================

    def process_acceleration(
        self,
        x,
        y,
        z
    ):

        if not self.running:
            return

        magnitude = math.sqrt(
            (x * x) +
            (y * y) +
            (z * z)
        )

        # Strong movement.
        if magnitude >= self.threshold:

            self.strong_hits += 1

        else:

            # Decay.
            self.strong_hits = max(
                0,
                self.strong_hits - 1
            )

        if (
            self.strong_hits
            >=
            self.required_hits
        ):

            self.strong_hits = 0

            self.trigger_sos()

    # ==========================================================
    # TRIGGER
    # ==========================================================

    def trigger_sos(self):

        now = time.monotonic()

        with self._lock:

            if (
                now - self.last_trigger
                <
                self.cooldown
            ):

                return False

            self.last_trigger = now

        print(
            "SHAKE DETECTION: SOS TRIGGERED"
        )

        if not self.callback:

            return False

        Clock.schedule_once(
            lambda dt:
            self._run_callback(),
            0
        )

        return True

    # ==========================================================
    # CALLBACK
    # ==========================================================

    def _run_callback(self):

        try:

            if self.callback:

                self.callback()

        except Exception as e:

            print(
                "Shake SOS callback error:",
                e
            )

    # ==========================================================
    # TEST
    # ==========================================================

    def test_trigger(self):

        return self.trigger_sos()

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self):

        if not self.running:

            return True

        if platform == "android":

            try:

                if (
                    self.sensor_manager
                    and
                    self.sensor_listener
                ):

                    self.sensor_manager.unregisterListener(
                        self.sensor_listener
                    )

            except Exception as e:

                print(
                    "Shake stop error:",
                    e
                )

        self.sensor_listener = None
        self.running = False
        self.strong_hits = 0

        print(
            "Shake detection: STOPPED"
        )

        return True

    # ==========================================================
    # RELEASE
    # ==========================================================

    def release(self):

        self.stop()

        self.activity = None
        self.sensor_manager = None
        self.sensor = None
        self.available = False

    # ==========================================================
    # STATUS
    # ==========================================================

    def is_available(self):

        return self.available

    def is_running(self):

        return self.running