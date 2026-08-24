# modules/sos.py

import json
import os
from datetime import datetime
from urllib.parse import quote

from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.utils import platform

from kivymd.toast import toast
from kivymd.uix.screen import MDScreen

from modules.siren import SirenManager


class SOSScreen(MDScreen):

    # ==========================================================
    # UI PROPERTIES
    # ==========================================================

    status_text = StringProperty("Press START SOS")
    siren_status = StringProperty("Siren OFF")
    siren_button_text = StringProperty("START SIREN")
    step_index = NumericProperty(0)

    # ==========================================================
    # SOS WORKFLOW
    # ==========================================================

    steps = [
        "Live Location",
        "Capture Photo",
        "Record Video",
        "Record Audio",
        "Load Contacts",
        "Send Alert",
        "Nearby Police",
        "SOS Completed",
    ]

    # ==========================================================
    # BASE / DATA DIRECTORY
    # ==========================================================

    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    DATA_DIR = os.path.join(
        BASE_DIR,
        "data"
    )

    HISTORY_FILE = os.path.join(
        DATA_DIR,
        "history.json"
    )

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.cancelled = False
        self.sos_running = False
        self.workflow_event = None

        self.contacts = []

        # Current location
        self.current_latitude = ""
        self.current_longitude = ""

        # ======================================================
        # SIREN
        # ======================================================

        try:
            self.siren = SirenManager()
        except Exception as error:
            print("Siren initialization error:", error)
            self.siren = None

        # ======================================================
        # OPTIONAL MODULES
        # ======================================================

        self.flashlight = None
        self.vibrator = None
        self.sms = None
        self.voice = None
        self.shake = None

        self._load_optional_modules()

    # ==========================================================
    # LOAD OPTIONAL MODULES
    # ==========================================================

    def _load_optional_modules(self):

        # ------------------------------------------------------
        # FLASHLIGHT
        # ------------------------------------------------------

        try:
            from modules.android_flashlight import AndroidFlashlight

            self.flashlight = AndroidFlashlight()

            print("Flashlight module loaded")

        except Exception as error:
            self.flashlight = None
            print("Flashlight module unavailable:", error)

        # ------------------------------------------------------
        # VIBRATOR
        # ------------------------------------------------------

        try:
            from modules.android_vibrator import AndroidVibrator

            self.vibrator = AndroidVibrator()

            print("Vibrator module loaded")

        except Exception as error:
            self.vibrator = None
            print("Vibrator module unavailable:", error)

        # ------------------------------------------------------
        # SMS
        # ------------------------------------------------------

        try:
            from modules.android_sms import AndroidSMS

            self.sms = AndroidSMS()

            print("SMS module loaded")

        except Exception as error:
            self.sms = None
            print("SMS module unavailable:", error)

        # ------------------------------------------------------
        # VOICE
        # ------------------------------------------------------

        try:
            from modules.voice_command import VoiceCommand

            self.voice = VoiceCommand(
                sos_callback=self.start_sos
            )

            print("Voice command module loaded")

        except Exception as error:
            self.voice = None
            print("Voice command unavailable:", error)

        # ------------------------------------------------------
        # SHAKE
        # ------------------------------------------------------

        try:
            from modules.shake_detection import ShakeDetection

            self.shake = ShakeDetection(
                callback=self.start_sos
            )

            print("Shake detection module loaded")

        except Exception as error:
            self.shake = None
            print("Shake detection unavailable:", error)

    # ==========================================================
    # SCREEN ENTER
    # ==========================================================

    def on_enter(self):

        print("SOS screen entered")

        self.reset_ui_only()

        # Start voice command
        if self.voice:

            try:
                self.voice.start()

            except Exception as error:
                print("Voice start error:", error)

        # Start shake detection
        if self.shake:

            try:
                self.shake.start()

            except Exception as error:
                print("Shake detection start error:", error)

    # ==========================================================
    # SCREEN LEAVE
    # ==========================================================

    def on_leave(self):

        # Voice OFF
        if self.voice:

            try:
                self.voice.stop()

            except Exception as error:
                print("Voice stop error:", error)

        # Shake OFF
        if self.shake:

            try:
                self.shake.stop()

            except Exception as error:
                print("Shake stop error:", error)

        # Siren OFF
        self.stop_siren()

        # Flashlight OFF
        self._turn_flashlight_off()

    # ==========================================================
    # RESET UI
    # ==========================================================

    def reset_ui_only(self):

        self.status_text = "Press START SOS"
        self.siren_status = "Siren OFF"
        self.siren_button_text = "START SIREN"

        self.step_index = 0

        self.cancelled = False
        self.sos_running = False
        self.workflow_event = None

    # ==========================================================
    # SIREN BUTTON
    # ==========================================================

    def siren_pressed(self):

        if self.siren is None:

            toast("Siren module unavailable")
            return

        try:

            if self.siren.is_playing:

                self.stop_siren()
                toast("Siren OFF")

            else:

                self.start_siren()

        except Exception as error:

            print("Siren button error:", error)
            toast("Unable to control siren")

    # ==========================================================
    # START SIREN
    # ==========================================================

    def start_siren(self):

        if self.siren is None:

            self.siren_status = "Siren unavailable"
            self.siren_button_text = "START SIREN"

            return False

        try:

            started = self.siren.start()

            if started:

                self.siren_status = "Siren ON"
                self.siren_button_text = "STOP SIREN"

                self.save_history("Siren ON")

                return True

        except Exception as error:

            print("Siren start error:", error)

        self.siren_status = "Siren unavailable"
        self.siren_button_text = "START SIREN"

        return False

    # ==========================================================
    # STOP SIREN
    # ==========================================================

    def stop_siren(self):

        if self.siren is None:

            self.siren_status = "Siren OFF"
            self.siren_button_text = "START SIREN"

            return

        try:
            self.siren.stop()

        except Exception as error:
            print("Siren stop error:", error)

        self.siren_status = "Siren OFF"
        self.siren_button_text = "START SIREN"

    # ==========================================================
    # FLASHLIGHT OFF
    # ==========================================================

    def _turn_flashlight_off(self):

        if self.flashlight:

            try:
                self.flashlight.turn_off()

            except Exception as error:
                print("Flashlight OFF error:", error)

    # ==========================================================
    # START SOS
    # ==========================================================

    def start_sos(self, *args):

        if self.sos_running:

            toast("SOS is already running")
            return

        print("================================")
        print("SAFIVOX SOS ACTIVATED")
        print("Platform:", platform)
        print("================================")

        self.cancel_workflow()

        self.cancelled = False
        self.sos_running = True
        self.step_index = 0

        # ======================================================
        # FLASHLIGHT
        # ======================================================

        if self.flashlight:

            try:

                result = self.flashlight.turn_on()

                print("Flashlight result:", result)

                self.save_history("Flashlight ON")

            except Exception as error:

                print("Flashlight error:", error)

                self.save_history(
                    f"Flashlight Error: {error}"
                )

        # ======================================================
        # VIBRATION
        # ======================================================

        if self.vibrator:

            try:

                if hasattr(
                    self.vibrator,
                    "vibrate_pattern"
                ):

                    self.vibrator.vibrate_pattern()

                elif hasattr(
                    self.vibrator,
                    "vibrate"
                ):

                    self.vibrator.vibrate(1000)

                self.save_history(
                    "Vibration Started"
                )

            except Exception as error:

                print("Vibrator error:", error)

        # ======================================================
        # SIREN
        # ======================================================

        self.start_siren()

        # ======================================================
        # UI
        # ======================================================

        self.status_text = "SOS Activated"

        self.save_history("SOS Activated")

        toast("Emergency SOS Activated")

        # ======================================================
        # START WORKFLOW
        # ======================================================

        Clock.schedule_once(
            self.run_steps,
            0.2
        )

    # ==========================================================
    # RUN SOS STEPS
    # ==========================================================

    def run_steps(self, dt=None):

        if self.cancelled:
            return False

        if not self.sos_running:
            return False

        # Completed
        if self.step_index >= len(self.steps):

            self.finish_sos()
            return False

        current_step = self.steps[
            self.step_index
        ]

        self.status_text = current_step

        print(
            "SOS STEP:",
            current_step
        )

        success = self.execute_step(
            current_step
        )

        if not success:

            self.save_history(
                f"{current_step} Failed"
            )

        self.step_index += 1

        if self.step_index >= len(
            self.steps
        ):

            self.finish_sos()
            return False

        self.workflow_event = Clock.schedule_once(
            self.run_steps,
            1.0
        )

        return False

    # ==========================================================
    # EXECUTE STEP
    # ==========================================================

    def execute_step(self, step):

        try:

            if step == "Live Location":
                return self.workflow_location()

            if step == "Capture Photo":
                return self.workflow_photo()

            if step == "Record Video":
                return self.workflow_video()

            if step == "Record Audio":
                return self.workflow_audio()

            if step == "Load Contacts":
                return self.workflow_contacts()

            if step == "Send Alert":
                return self.workflow_sms()

            if step == "Nearby Police":
                return self.workflow_police()

            if step == "SOS Completed":
                return True

        except Exception as error:

            print(
                f"{step} error:",
                error
            )

            self.save_history(
                f"{step} Error: {error}"
            )

        return False

    # ==========================================================
    # LIVE LOCATION
    # ==========================================================

    def workflow_location(self):

        print("================================")
        print("STARTING LIVE GPS")
        print("================================")

        # ------------------------------------------------------
        # First use the existing LocationScreen
        # ------------------------------------------------------

        if self.manager:

            try:

                location_screen = self.manager.get_screen(
                    "location"
                )

                # Try existing start_gps()
                if hasattr(
                    location_screen,
                    "start_gps"
                ):

                    try:

                        result = location_screen.start_gps()

                        print(
                            "LocationScreen.start_gps():",
                            result
                        )

                        # Give GPS some time to update.
                        Clock.schedule_once(
                            self._read_location_after_start,
                            2.0
                        )

                        self.save_history(
                            "Live Location Started"
                        )

                        return True

                    except Exception as error:

                        print(
                            "Location screen GPS error:",
                            error
                        )

            except Exception as error:

                print(
                    "Location screen error:",
                    error
                )

        # ------------------------------------------------------
        # Android fallback GPS
        # ------------------------------------------------------

        if platform == "android":

            return self._start_android_gps()

        self.save_history(
            "GPS unavailable on this platform"
        )

        toast(
            "GPS works on Android"
        )

        return False

    # ==========================================================
    # READ LOCATION AFTER GPS START
    # ==========================================================

    def _read_location_after_start(self, dt):

        if not self.manager:
            return

        try:

            location = self.manager.get_screen(
                "location"
            )

            latitude = getattr(
                location,
                "latitude",
                ""
            )

            longitude = getattr(
                location,
                "longitude",
                ""
            )

            if latitude and longitude:

                self.current_latitude = str(
                    latitude
                )

                self.current_longitude = str(
                    longitude
                )

                print(
                    "CURRENT LOCATION:",
                    self.current_latitude,
                    self.current_longitude
                )

                self.save_history(
                    "Location: "
                    f"{self.current_latitude}, "
                    f"{self.current_longitude}"
                )

                self.status_text = (
                    "Location received"
                )

            else:

                print(
                    "GPS started but coordinates not received yet"
                )

                self.save_history(
                    "GPS started - waiting for coordinates"
                )

        except Exception as error:

            print(
                "Location read error:",
                error
            )

    # ==========================================================
    # ANDROID GPS FALLBACK
    # ==========================================================

    def _start_android_gps(self):

        try:

            from android.permissions import (
                request_permissions,
                Permission
            )

            request_permissions(
                [
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ]
            )

            print(
                "Android location permission requested"
            )

        except Exception as error:

            print(
                "Android permission error:",
                error
            )

        try:

            from plyer import gps

            gps.configure(
                on_location=self._on_gps_location,
                on_status=self._on_gps_status
            )

            gps.start(
                minTime=1000,
                minDistance=1
            )

            self.save_history(
                "Android GPS Started"
            )

            toast(
                "Getting current location..."
            )

            return True

        except Exception as error:

            print(
                "Android GPS error:",
                error
            )

            self.save_history(
                f"Android GPS Error: {error}"
            )

            return False

    # ==========================================================
    # GPS LOCATION CALLBACK
    # ==========================================================

    def _on_gps_location(
        self,
        **kwargs
    ):

        latitude = kwargs.get(
            "lat",
            ""
        )

        longitude = kwargs.get(
            "lon",
            ""
        )

        if not latitude or not longitude:
            return

        self.current_latitude = str(
            latitude
        )

        self.current_longitude = str(
            longitude
        )

        print(
            "GPS CALLBACK:",
            self.current_latitude,
            self.current_longitude
        )

        Clock.schedule_once(
            lambda dt: self._update_location_ui(),
            0
        )

    # ==========================================================
    # GPS STATUS CALLBACK
    # ==========================================================

    def _on_gps_status(
        self,
        **kwargs
    ):

        print(
            "GPS STATUS:",
            kwargs
        )

    # ==========================================================
    # UPDATE LOCATION UI
    # ==========================================================

    def _update_location_ui(self):

        self.save_history(
            "Current Location: "
            f"{self.current_latitude}, "
            f"{self.current_longitude}"
        )

        self.status_text = (
            "Current Location Received"
        )

    # ==========================================================
    # STOP GPS
    # ==========================================================

    def stop_gps(self):

        if platform != "android":
            return

        try:

            from plyer import gps

            gps.stop()

            print(
                "GPS stopped"
            )

        except Exception as error:

            print(
                "GPS stop error:",
                error
            )

    # ==========================================================
    # PHOTO
    # ==========================================================

    def workflow_photo(self):

        if not self.manager:
            return False

        try:

            evidence = self.manager.get_screen(
                "evidence"
            )

        except Exception as error:

            print(
                "Evidence screen error:",
                error
            )

            return False

        if not hasattr(
            evidence,
            "take_photo"
        ):

            self.save_history(
                "Photo Module Unavailable"
            )

            return False

        try:

            photo = evidence.take_photo()

            if photo:

                self.save_history(
                    f"Photo Captured: {photo}"
                )

                return True

        except Exception as error:

            print(
                "Photo error:",
                error
            )

        return False

    # ==========================================================
    # VIDEO
    # ==========================================================

    def workflow_video(self):

        if not self.manager:
            return False

        try:

            evidence = self.manager.get_screen(
                "evidence"
            )

            if not hasattr(
                evidence,
                "record_video"
            ):

                self.save_history(
                    "Video Module Unavailable"
                )

                return False

            video = evidence.record_video()

            if video:

                self.save_history(
                    f"Video Recorded: {video}"
                )

                return True

        except Exception as error:

            print(
                "Video error:",
                error
            )

        return False

    # ==========================================================
    # AUDIO
    # ==========================================================

    def workflow_audio(self):

        if not self.manager:
            return False

        try:

            evidence = self.manager.get_screen(
                "evidence"
            )

            if not hasattr(
                evidence,
                "record_audio"
            ):

                self.save_history(
                    "Audio Module Unavailable"
                )

                return False

            audio = evidence.record_audio()

            if audio:

                self.save_history(
                    f"Audio Recorded: {audio}"
                )

                return True

        except Exception as error:

            print(
                "Audio error:",
                error
            )

        return False

    # ==========================================================
    # LOAD CONTACTS
    # ==========================================================

    def workflow_contacts(self):

        if not self.manager:
            return False

        try:

            contacts_screen = self.manager.get_screen(
                "contacts"
            )

        except Exception as error:

            print(
                "Contacts screen error:",
                error
            )

            return False

        # ------------------------------------------------------
        # Try ContactsScreen.read_contacts()
        # ------------------------------------------------------

        if hasattr(
            contacts_screen,
            "read_contacts"
        ):

            try:

                contacts = contacts_screen.read_contacts()

                if contacts is None:
                    contacts = []

                self.contacts = contacts

                self.save_history(
                    f"{len(self.contacts)} "
                    "Emergency Contacts Loaded"
                )

                return bool(
                    self.contacts
                )

            except Exception as error:

                print(
                    "Read contacts error:",
                    error
                )

        # ------------------------------------------------------
        # JSON fallback
        # ------------------------------------------------------

        contact_file = os.path.join(
            self.DATA_DIR,
            "emergency_contacts.json"
        )

        try:

            if not os.path.exists(
                contact_file
            ):

                self.contacts = []

                self.save_history(
                    "No emergency contacts file"
                )

                return False

            with open(
                contact_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if isinstance(
                data,
                list
            ):

                self.contacts = data

            else:

                self.contacts = []

            self.save_history(
                f"{len(self.contacts)} "
                "Emergency Contacts Loaded"
            )

            print(
                "Loaded contacts:",
                self.contacts
            )

            return bool(
                self.contacts
            )

        except Exception as error:

            print(
                "Contact loading error:",
                error
            )

            return False

    # ==========================================================
    # SEND SMS
    # ==========================================================

    def workflow_sms(self):

        if not self.contacts:

            self.save_history(
                "No Emergency Contacts"
            )

            toast(
                "No emergency contacts saved"
            )

            return False

        if self.sms is None:

            self.save_history(
                "SMS Module Unavailable"
            )

            toast(
                "SMS unavailable"
            )

            return False

        location_link = self.get_location_link()

        message = (
            "SAFIVOX EMERGENCY ALERT\n\n"
            "I need help.\n\n"
            "My current location:\n"
            f"{location_link}\n\n"
            "This message was generated "
            "by Safivox."
        )

        sent_count = 0

        for contact in self.contacts:

            if not isinstance(
                contact,
                dict
            ):
                continue

            name = contact.get(
                "name",
                "Emergency Contact"
            )

            phone = contact.get(
                "phone",
                ""
            )

            if not phone:
                continue

            try:

                self.sms.send_sms(
                    phone,
                    message
                )

                sent_count += 1

                self.save_history(
                    f"SMS Sent to {name}"
                )

                print(
                    f"SMS sent to {name}: {phone}"
                )

            except Exception as error:

                print(
                    f"SMS error for {name}:",
                    error
                )

                self.save_history(
                    f"SMS Failed for {name}: "
                    f"{error}"
                )

        if sent_count > 0:

            toast(
                f"Alert sent to "
                f"{sent_count} contact(s)"
            )

            return True

        return False

    # ==========================================================
    # GET LOCATION LINK
    # ==========================================================

    def get_location_link(self):

        # ------------------------------------------------------
        # Our stored GPS coordinates
        # ------------------------------------------------------

        if (
            self.current_latitude
            and self.current_longitude
        ):

            return (
                "https://www.google.com/maps"
                "?q="
                f"{self.current_latitude},"
                f"{self.current_longitude}"
            )

        # ------------------------------------------------------
        # Location screen coordinates
        # ------------------------------------------------------

        if self.manager:

            try:

                location = self.manager.get_screen(
                    "location"
                )

                # Existing get_map_link()
                if hasattr(
                    location,
                    "get_map_link"
                ):

                    try:

                        link = location.get_map_link()

                        if link:
                            return link

                    except Exception as error:

                        print(
                            "Map link error:",
                            error
                        )

                latitude = getattr(
                    location,
                    "latitude",
                    ""
                )

                longitude = getattr(
                    location,
                    "longitude",
                    ""
                )

                if latitude and longitude:

                    return (
                        "https://www.google.com/maps"
                        "?q="
                        f"{latitude},"
                        f"{longitude}"
                    )

            except Exception as error:

                print(
                    "Location screen error:",
                    error
                )

        return "Location unavailable"

    # ==========================================================
    # NEARBY POLICE
    # ==========================================================

    def workflow_police(self):

        print(
            "================================"
        )

        print(
            "OPENING NEARBY POLICE"
        )

        print(
            "================================"
        )

        # ------------------------------------------------------
        # First try LocationScreen.nearby_police()
        # ------------------------------------------------------

        if self.manager:

            try:

                location = self.manager.get_screen(
                    "location"
                )

                if hasattr(
                    location,
                    "nearby_police"
                ):

                    try:

                        result = location.nearby_police()

                        if result:

                            self.save_history(
                                "Nearby Police Opened"
                            )

                            return True

                    except Exception as error:

                        print(
                            "LocationScreen nearby police error:",
                            error
                        )

            except Exception as error:

                print(
                    "Location screen error:",
                    error
                )

        # ------------------------------------------------------
        # Android / external Maps fallback
        # ------------------------------------------------------

        try:

            maps_query = quote(
                "police station near me"
            )

            maps_url = (
                "https://www.google.com/maps/search/"
                f"?api=1&query={maps_query}"
            )

            if platform == "android":

                from jnius import autoclass

                PythonActivity = autoclass(
                    "org.kivy.android.PythonActivity"
                )

                Intent = autoclass(
                    "android.content.Intent"
                )

                Uri = autoclass(
                    "android.net.Uri"
                )

                intent = Intent(
                    Intent.ACTION_VIEW,
                    Uri.parse(maps_url)
                )

                current_activity = (
                    PythonActivity.mActivity
                )

                current_activity.startActivity(
                    intent
                )

                self.save_history(
                    "Nearby Police Opened in Google Maps"
                )

                toast(
                    "Nearby police stations opened"
                )

                return True

            # Windows / development fallback
            else:

                import webbrowser

                webbrowser.open(
                    maps_url
                )

                self.save_history(
                    "Nearby Police Opened in Browser"
                )

                return True

        except Exception as error:

            print(
                "Nearby police fallback error:",
                error
            )

            self.save_history(
                f"Nearby Police Failed: {error}"
            )

        return False

    # ==========================================================
    # FINISH SOS
    # ==========================================================

    def finish_sos(self):

        self.cancel_workflow()

        self.sos_running = False

        self.status_text = "SOS Completed"

        # GPS
        self.stop_gps()

        # Siren
        self.stop_siren()

        # Flashlight
        self._turn_flashlight_off()

        # Vibration
        if self.vibrator:

            try:

                if hasattr(
                    self.vibrator,
                    "cancel"
                ):

                    self.vibrator.cancel()

            except Exception as error:

                print(
                    "Vibration cancel error:",
                    error
                )

        self.save_history(
            "SOS Completed"
        )

        toast(
            "SOS Completed Successfully"
        )

    # ==========================================================
    # CANCEL SOS
    # ==========================================================

    def cancel_sos(self):

        self.cancelled = True
        self.sos_running = False

        self.cancel_workflow()

        # GPS
        self.stop_gps()

        # Siren
        self.stop_siren()

        # Flashlight
        if self.flashlight:

            try:

                self.flashlight.turn_off()

                self.save_history(
                    "Flashlight OFF"
                )

            except Exception as error:

                print(
                    "Flashlight OFF error:",
                    error
                )

        # Vibration
        if self.vibrator:

            try:

                if hasattr(
                    self.vibrator,
                    "cancel"
                ):

                    self.vibrator.cancel()

            except Exception as error:

                print(
                    "Vibration cancel error:",
                    error
                )

        self.status_text = "SOS Cancelled"

        self.step_index = 0

        self.save_history(
            "SOS Cancelled"
        )

        toast(
            "SOS Cancelled"
        )

    # ==========================================================
    # CANCEL WORKFLOW
    # ==========================================================

    def cancel_workflow(self):

        if self.workflow_event is not None:

            try:
                self.workflow_event.cancel()

            except Exception:
                pass

            self.workflow_event = None

    # ==========================================================
    # BACK ARROW
    # ==========================================================

    def go_back(self, *args):

        print(
            "SOS back button pressed"
        )

        # Stop active SOS
        if self.sos_running:

            self.cancel_sos()

        else:

            self.cancel_workflow()
            self.stop_siren()
            self.stop_gps()

            if self.flashlight:

                try:
                    self.flashlight.turn_off()

                except Exception:
                    pass

        # ------------------------------------------------------
        # Return HOME
        # ------------------------------------------------------

        try:

            if self.manager is not None:

                if self.manager.has_screen(
                    "home"
                ):

                    self.manager.current = "home"

                    print(
                        "Returned to Home screen"
                    )

                    return True

        except Exception as error:

            print(
                "Unable to return home:",
                error
            )

        return False

    # ==========================================================
    # HISTORY
    # ==========================================================

    def save_history(self, event):

        try:

            os.makedirs(
                self.DATA_DIR,
                exist_ok=True
            )

            history = []

            if os.path.exists(
                self.HISTORY_FILE
            ):

                try:

                    with open(
                        self.HISTORY_FILE,
                        "r",
                        encoding="utf-8"
                    ) as file:

                        data = json.load(file)

                    if isinstance(
                        data,
                        list
                    ):

                        history = data

                except Exception:

                    history = []

            history.append(
                {
                    "time":
                        datetime.now().strftime(
                            "%d-%m-%Y %H:%M:%S"
                        ),

                    "event":
                        str(event)
                }
            )

            history = history[-500:]

            with open(
                self.HISTORY_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    history,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as error:

            print(
                "History save error:",
                error
            )

    # ==========================================================
    # GET HISTORY
    # ==========================================================

    def get_history(self):

        if not os.path.exists(
            self.HISTORY_FILE
        ):

            return []

        try:

            with open(
                self.HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if isinstance(
                data,
                list
            ):

                return data

        except Exception as error:

            print(
                "History read error:",
                error
            )

        return []

    # ==========================================================
    # CLEAR HISTORY
    # ==========================================================

    def clear_history(self):

        try:

            os.makedirs(
                self.DATA_DIR,
                exist_ok=True
            )

            with open(
                self.HISTORY_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    [],
                    file,
                    indent=4
                )

            toast(
                "History Cleared"
            )

        except Exception as error:

            print(
                "History clear error:",
                error
            )

            toast(
                "Unable to clear history"
            )