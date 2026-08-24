"""
Safivox Android Phone Call Module

Purpose:
    Make a direct phone call to an emergency contact on Android.

Android:
    Uses PyJNIus + Android Intent.

Desktop:
    Does not attempt to make a phone call.
    It simply prints a message and returns False.
"""

import re


class AndroidCall:
    """Android phone-call helper."""

    @staticmethod
    def clean_phone_number(phone_number):
        """
        Clean a phone number before sending it to Android.
        """

        if phone_number is None:
            return ""

        phone_number = str(phone_number).strip()

        # Keep digits and leading +
        cleaned = re.sub(r"[^\d+]", "", phone_number)

        # Prevent multiple + symbols
        if "+" in cleaned:
            cleaned = "+" + cleaned.replace("+", "")

        return cleaned

    @staticmethod
    def is_android():
        """
        Check whether the application is running on Android.
        """

        try:
            from android import mActivity
            return mActivity is not None
        except Exception:
            return False

    @staticmethod
    def make_call(phone_number):
        """
        Make a direct phone call on Android.

        Returns:
            True  -> call request successfully sent
            False -> unable to start call
        """

        phone_number = AndroidCall.clean_phone_number(phone_number)

        if not phone_number:
            print("Call error: Phone number is empty.")
            return False

        # --------------------------------------------------
        # DESKTOP / WINDOWS
        # --------------------------------------------------

        if not AndroidCall.is_android():

            print(
                "Phone call unavailable on desktop."
            )

            print(
                "Call requested for:",
                phone_number
            )

            return False

        # --------------------------------------------------
        # ANDROID
        # --------------------------------------------------

        try:

            from jnius import autoclass

            # Android classes
            Intent = autoclass(
                "android.content.Intent"
            )

            Uri = autoclass(
                "android.net.Uri"
            )

            # Current Android activity
            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity = (
                PythonActivity.mActivity
            )

            # Create telephone URI
            uri = Uri.parse(
                "tel:" + phone_number
            )

            # ACTION_CALL = direct phone call
            intent = Intent(
                Intent.ACTION_CALL,
                uri
            )

            # Start phone call
            activity.startActivity(intent)

            print(
                "Calling emergency contact:",
                phone_number
            )

            return True

        except Exception as error:

            print(
                "Android call error:",
                error
            )

            return False


# ----------------------------------------------------------
# SIMPLE FUNCTION
# ----------------------------------------------------------

def make_call(phone_number):
    """
    Simple function that can be imported elsewhere.
    """

    return AndroidCall.make_call(
        phone_number
    )