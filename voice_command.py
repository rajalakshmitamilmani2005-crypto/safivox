import threading
import time

from kivy.clock import Clock
from kivy.utils import platform


class VoiceCommand:
    """
    Safivox voice-command controller.

    Compatible with:

        VoiceCommand(
            sos_callback=self.start_sos
        )
    """

    EMERGENCY_PHRASES = (
        "sos",
        "emergency",
        "help me",
        "i need help",
        "save me",
        "please help",
    )

    def __init__(
        self,
        sos_callback=None,
        phrases=None,
        cooldown=8.0
    ):

        self.sos_callback = sos_callback

        self.phrases = tuple(
            phrases
            if phrases is not None
            else self.EMERGENCY_PHRASES
        )

        self.cooldown = float(
            cooldown
        )

        self.running = False
        self.available = False

        self.last_trigger = 0.0

        self._lock = threading.RLock()

        # Android
        self.speech_recognizer = None
        self.recognition_listener = None
        self.recognizer_intent = None

        # Windows fallback
        self.desktop_recognizer = None
        self.desktop_microphone = None
        self.desktop_thread = None

    # ==========================================================
    # START
    # ==========================================================

    def start(self):

        if self.running:
            return True

        if platform == "android":
            return self._start_android()

        return self._start_desktop()

    # ==========================================================
    # ANDROID START
    # ==========================================================

    def _start_android(self):

        try:

            from jnius import (
                PythonJavaClass,
                autoclass,
                java_method,
            )

            SpeechRecognizer = autoclass(
                "android.speech.SpeechRecognizer"
            )

            RecognitionListener = (
                "android.speech.RecognitionListener"
            )

            RecognizerIntent = autoclass(
                "android.speech.RecognizerIntent"
            )

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            Context = autoclass(
                "android.content.Context"
            )

            if not SpeechRecognizer.isRecognitionAvailable(
                PythonActivity.mActivity
            ):
                print(
                    "Voice command: Android speech recognition unavailable."
                )
                return False

            owner = self

            class Listener(PythonJavaClass):

                __javainterfaces__ = [
                    "android/speech/RecognitionListener"
                ]

                @java_method("()V")
                def onReadyForSpeech(self, params):
                    pass

                @java_method("()V")
                def onBeginningOfSpeech(self):
                    pass

                @java_method("([B)V")
                def onBufferReceived(self, buffer):
                    pass

                @java_method("(F)V")
                def onRmsChanged(self, rmsdB):
                    pass

                @java_method("()V")
                def onEndOfSpeech(self):
                    pass

                @java_method("(I)V")
                def onError(self, error):
                    # Restart listening after a short delay.
                    if owner.running:
                        Clock.schedule_once(
                            lambda dt:
                            owner._restart_android_listener(),
                            0.5
                        )

                @java_method(
                    "(Landroid/os/Bundle;)V"
                )
                def onResults(self, results):

                    try:

                        matches = results.getStringArrayList(
                            "results_recognition"
                        )

                        if matches:

                            for i in range(
                                matches.size()
                            ):

                                text = str(
                                    matches.get(i)
                                )

                                print(
                                    "Voice recognized:",
                                    text
                                )

                                if owner.is_emergency_phrase(
                                    text
                                ):

                                    owner.trigger_sos(
                                        text
                                    )

                                    break

                    except Exception as e:

                        print(
                            "Voice result error:",
                            e
                        )

                    if owner.running:

                        Clock.schedule_once(
                            lambda dt:
                            owner._restart_android_listener(),
                            0.2
                        )

                @java_method(
                    "(Landroid/os/Bundle;)V"
                )
                def onPartialResults(
                    self,
                    partial_results
                ):
                    pass

                @java_method(
                    "(ILandroid/os/Bundle;)V"
                )
                def onEvent(
                    self,
                    event_type,
                    params
                ):
                    pass

            self.recognition_listener = Listener()

            self.speech_recognizer = (
                SpeechRecognizer.createSpeechRecognizer(
                    PythonActivity.mActivity
                )
            )

            self.speech_recognizer.setRecognitionListener(
                self.recognition_listener
            )

            intent = autoclass(
                "android.content.Intent"
            )(
                RecognizerIntent.ACTION_RECOGNIZE_SPEECH
            )

            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )

            intent.putExtra(
                RecognizerIntent.EXTRA_PARTIAL_RESULTS,
                False
            )

            intent.putExtra(
                RecognizerIntent.EXTRA_MAX_RESULTS,
                5
            )

            self.recognizer_intent = intent

            self.running = True
            self.available = True

            self._restart_android_listener()

            print(
                "Voice command: Android listener started."
            )

            return True

        except Exception as e:

            print(
                "Android voice initialization error:",
                e
            )

            self.running = False
            self.available = False

            return False

    # ==========================================================
    # RESTART ANDROID LISTENER
    # ==========================================================

    def _restart_android_listener(self):

        if not self.running:
            return

        if (
            self.speech_recognizer is None
            or
            self.recognizer_intent is None
        ):
            return

        try:

            self.speech_recognizer.startListening(
                self.recognizer_intent
            )

        except Exception as e:

            print(
                "Android speech restart error:",
                e
            )

            if self.running:

                Clock.schedule_once(
                    lambda dt:
                    self._restart_android_listener(),
                    1.0
                )

    # ==========================================================
    # WINDOWS FALLBACK
    # ==========================================================

    def _start_desktop(self):

        try:

            import speech_recognition as sr

        except ImportError:

            print(
                "Voice command unavailable on Windows: "
                "SpeechRecognition is not installed."
            )

            self.available = False

            return False

        try:

            self.desktop_recognizer = (
                sr.Recognizer()
            )

            self.desktop_microphone = (
                sr.Microphone()
            )

            # Ambient noise calibration
            try:

                with self.desktop_microphone as source:

                    self.desktop_recognizer.adjust_for_ambient_noise(
                        source,
                        duration=0.7
                    )

            except Exception as e:

                print(
                    "Voice calibration warning:",
                    e
                )

            self.running = True
            self.available = True

            self.desktop_thread = threading.Thread(
                target=self._desktop_listen_loop,
                daemon=True
            )

            self.desktop_thread.start()

            print(
                "Voice command: desktop listener started."
            )

            return True

        except Exception as e:

            print(
                "Desktop voice initialization error:",
                e
            )

            self.running = False
            self.available = False

            return False

    # ==========================================================
    # DESKTOP LISTENER
    # ==========================================================

    def _desktop_listen_loop(self):

        import speech_recognition as sr

        while self.running:

            try:

                with self.desktop_microphone as source:

                    audio = (
                        self.desktop_recognizer.listen(
                            source,
                            timeout=2,
                            phrase_time_limit=4
                        )
                    )

                if not self.running:
                    break

                try:

                    text = (
                        self.desktop_recognizer
                        .recognize_google(
                            audio
                        )
                    )

                except (
                    sr.UnknownValueError,
                    sr.RequestError,
                ):

                    continue

                if not text:
                    continue

                print(
                    "Desktop voice:",
                    text
                )

                if self.is_emergency_phrase(
                    text
                ):

                    self.trigger_sos(
                        text
                    )

            except sr.WaitTimeoutError:

                continue

            except Exception as e:

                if self.running:

                    print(
                        "Desktop voice error:",
                        e
                    )

                time.sleep(
                    0.2
                )

    # ==========================================================
    # CHECK EMERGENCY PHRASE
    # ==========================================================

    def is_emergency_phrase(
        self,
        text
    ):

        normalized = (
            str(text)
            .strip()
            .lower()
        )

        return any(
            phrase.lower() in normalized
            for phrase in self.phrases
        )

    # ==========================================================
    # TRIGGER SOS
    # ==========================================================

    def trigger_sos(
        self,
        recognized_text=""
    ):

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
            "VOICE SOS TRIGGER:",
            recognized_text
        )

        if not self.sos_callback:

            return False

        # Run SOS on the Kivy/UI thread.
        Clock.schedule_once(
            lambda dt:
            self._run_sos_callback(),
            0
        )

        return True

    # ==========================================================
    # CALLBACK
    # ==========================================================

    def _run_sos_callback(self):

        try:

            if self.sos_callback:

                self.sos_callback()

        except Exception as e:

            print(
                "Voice SOS callback error:",
                e
            )

    # ==========================================================
    # TEST
    # ==========================================================

    def trigger_test_sos(self):

        return self.trigger_sos(
            "test sos"
        )

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self):

        self.running = False

        if platform == "android":

            try:

                if self.speech_recognizer:

                    self.speech_recognizer.cancel()

            except Exception:
                pass

            try:

                if self.speech_recognizer:

                    self.speech_recognizer.destroy()

            except Exception:
                pass

            self.speech_recognizer = None
            self.recognition_listener = None
            self.recognizer_intent = None

        print(
            "Voice command: stopped."
        )

    # ==========================================================
    # RELEASE
    # ==========================================================

    def release(self):

        self.stop()

        self.available = False

    # ==========================================================
    # STATUS
    # ==========================================================

    def is_available(self):

        return (
            self.available
        )

    def is_running(self):

        return (
            self.running
        )