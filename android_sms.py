import threading

from kivy.utils import platform


class AndroidSMS:
    """
    Safivox Android SMS helper.

    Main method:
        send_sms(phone_number, message)

    On Android:
        Uses Android SmsManager.

    On Windows:
        Does not attempt to send a real SMS.
    """

    def __init__(self):

        self.available = False
        self.sms_manager = None

        self._lock = threading.RLock()

        if platform == "android":
            self._initialize_android()
        else:
            print(
                "Android SMS: unavailable on desktop."
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

            SmsManager = autoclass(
                "android.telephony.SmsManager"
            )

            activity = (
                PythonActivity.mActivity
            )

            # Android API compatibility.
            try:

                self.sms_manager = (
                    SmsManager.getDefault()
                )

            except Exception:

                self.sms_manager = (
                    activity.getSystemService(
                        Context.TELEPHONY_SERVICE
                    )
                )

            if self.sms_manager is None:

                print(
                    "Android SMS manager unavailable."
                )

                self.available = False

                return False

            self.available = True

            print(
                "Android SMS: initialized."
            )

            return True

        except Exception as e:

            print(
                "Android SMS initialization error:",
                e
            )

            self.sms_manager = None
            self.available = False

            return False

    # ==========================================================
    # SEND SMS
    # ==========================================================

    def send_sms(
        self,
        phone_number,
        message
    ):

        with self._lock:

            if not phone_number:

                print(
                    "SMS error: phone number is empty."
                )

                return False

            if not message:

                print(
                    "SMS error: message is empty."
                )

                return False

            phone_number = str(
                phone_number
            ).strip()

            message = str(
                message
            )

            # --------------------------------------------------
            # Desktop
            # --------------------------------------------------

            if platform != "android":

                print(
                    "--------------------------------"
                )

                print(
                    "[Desktop SMS Simulation]"
                )

                print(
                    "To:",
                    phone_number
                )

                print(
                    "Message:"
                )

                print(
                    message
                )

                print(
                    "--------------------------------"
                )

                return False

            # --------------------------------------------------
            # Android
            # --------------------------------------------------

            if not self.available:

                if not self._initialize_android():

                    return False

            try:

                # Short message:
                # sendTextMessage()
                #
                # Long message:
                # divideMessage() + sendMultipartTextMessage()

                if len(message) <= 160:

                    self.sms_manager.sendTextMessage(
                        phone_number,
                        None,
                        message,
                        None,
                        None
                    )

                else:

                    parts = (
                        self.sms_manager.divideMessage(
                            message
                        )
                    )

                    self.sms_manager.sendMultipartTextMessage(
                        phone_number,
                        None,
                        parts,
                        None,
                        None
                    )

                print(
                    "SMS sent:",
                    phone_number
                )

                return True

            except Exception as e:

                print(
                    "Android SMS send error:",
                    e
                )

                return False

    # ==========================================================
    # SEND TO MULTIPLE CONTACTS
    # ==========================================================

    def send_to_contacts(
        self,
        contacts,
        message
    ):

        sent = 0

        for contact in contacts:

            try:

                phone = contact.get(
                    "phone",
                    ""
                )

                if not phone:
                    continue

                if self.send_sms(
                    phone,
                    message
                ):

                    sent += 1

            except Exception as e:

                print(
                    "Contact SMS error:",
                    e
                )

        return sent

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

        self.sms_manager = None
        self.available = False