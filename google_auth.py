# ==========================================================
# SAFIVOX - GOOGLE AUTHENTICATION
# ==========================================================

from kivy.utils import platform


class GoogleAuth:

    def __init__(
        self,
        success_callback=None,
        error_callback=None
    ):

        self.success_callback = success_callback
        self.error_callback = error_callback

        self.is_android = (
            platform == "android"
        )

    # ======================================================
    # START GOOGLE SIGN-IN
    # ======================================================

    def sign_in(self):

        print(
            "================================"
        )

        print(
            "Safivox Google Sign-In"
        )

        print(
            "Platform:",
            platform
        )

        print(
            "================================"
        )

        # --------------------------------------------------
        # Windows / Desktop
        # --------------------------------------------------

        if not self.is_android:

            message = (
                "Google Sign-In is available "
                "in the Android APK."
            )

            print(
                message
            )

            self._error(
                message
            )

            return False

        # --------------------------------------------------
        # Android
        # --------------------------------------------------

        try:

            return self._android_google_sign_in()

        except Exception as error:

            print(
                "Google Sign-In error:",
                error
            )

            self._error(
                str(error)
            )

            return False

    # ======================================================
    # ANDROID GOOGLE SIGN-IN
    # ======================================================

    def _android_google_sign_in(self):

        """
        Native Android Google Sign-In entry point.

        This method will be connected to the
        Android Credential Manager implementation
        when building the APK.
        """

        try:

            from jnius import autoclass

            # ------------------------------------------------
            # Android context
            # ------------------------------------------------

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity = (
                PythonActivity.mActivity
            )

            print(
                "Android activity obtained:",
                activity
            )

            # ------------------------------------------------
            # IMPORTANT
            # ------------------------------------------------
            #
            # The actual Credential Manager /
            # Google Identity implementation needs
            # to be added to the Android build.
            #
            # Do not simply pretend authentication
            # succeeded.
            # ------------------------------------------------

            print(
                "Google Android authentication "
                "bridge is ready."
            )

            self._error(
                "Google Android authentication "
                "is not configured yet."
            )

            return False

        except ImportError:

            message = (
                "PyJNIus is not available."
            )

            print(
                message
            )

            self._error(
                message
            )

            return False

        except Exception as error:

            print(
                "Android Google bridge error:",
                error
            )

            self._error(
                str(error)
            )

            return False

    # ======================================================
    # SUCCESS
    # ======================================================

    def _success(
        self,
        user
    ):

        print(
            "Google authentication successful:"
        )

        print(
            user
        )

        if self.success_callback:

            try:

                self.success_callback(
                    user
                )

            except Exception as error:

                print(
                    "Google success callback error:",
                    error
                )

    # ======================================================
    # ERROR
    # ======================================================

    def _error(
        self,
        message
    ):

        if self.error_callback:

            try:

                self.error_callback(
                    message
                )

            except Exception as error:

                print(
                    "Google error callback error:",
                    error
                )