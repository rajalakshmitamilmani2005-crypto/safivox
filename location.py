import webbrowser

from kivy.clock import Clock
from kivy.utils import platform

from kivymd.uix.screen import MDScreen
from kivymd.toast import toast


# ==========================================================
# ANDROID IMPORTS
# ==========================================================

ANDROID = platform == "android"

if ANDROID:

    try:
        from android.permissions import (
            request_permissions,
            Permission
        )

        ANDROID_PERMISSION_AVAILABLE = True

    except Exception as error:

        print(
            "Android permission import error:",
            error
        )

        ANDROID_PERMISSION_AVAILABLE = False

else:

    ANDROID_PERMISSION_AVAILABLE = False


if ANDROID:

    try:

        from jnius import (
            autoclass,
            PythonJavaClass,
            java_method
        )

        PYJNIUS_AVAILABLE = True

    except Exception as error:

        print(
            "PyJNIus import error:",
            error
        )

        PYJNIUS_AVAILABLE = False

else:

    PYJNIUS_AVAILABLE = False


# ==========================================================
# ANDROID LOCATION LISTENER
# ==========================================================

if PYJNIUS_AVAILABLE:

    class AndroidLocationListener(
        PythonJavaClass
    ):

        __javainterfaces__ = [
            "android/location/LocationListener"
        ]

        __javacontext__ = "app"

        def __init__(
            self,
            screen
        ):

            super().__init__()

            self.screen = screen

        # --------------------------------------------------
        # LOCATION CHANGED
        # --------------------------------------------------

        @java_method(
            "(Landroid/location/Location;)V"
        )
        def onLocationChanged(
            self,
            location
        ):

            try:

                if location is None:
                    return

                latitude = (
                    location.getLatitude()
                )

                longitude = (
                    location.getLongitude()
                )

                self.screen.update_real_location(
                    latitude,
                    longitude
                )

            except Exception as error:

                print(
                    "Android location callback error:",
                    error
                )

        # --------------------------------------------------
        # PROVIDER ENABLED
        # --------------------------------------------------

        @java_method(
            "(Ljava/lang/String;)V"
        )
        def onProviderEnabled(
            self,
            provider
        ):

            print(
                "Location provider enabled:",
                provider
            )

        # --------------------------------------------------
        # PROVIDER DISABLED
        # --------------------------------------------------

        @java_method(
            "(Ljava/lang/String;)V"
        )
        def onProviderDisabled(
            self,
            provider
        ):

            print(
                "Location provider disabled:",
                provider
            )

        # --------------------------------------------------
        # STATUS CHANGED
        # --------------------------------------------------

        @java_method(
            "(Ljava/lang/String;ILandroid/os/Bundle;)V"
        )
        def onStatusChanged(
            self,
            provider,
            status,
            extras
        ):

            print(
                "Location status:",
                provider,
                status
            )


else:

    AndroidLocationListener = None


# ==========================================================
# LOCATION SCREEN
# ==========================================================

class LocationScreen(MDScreen):

    # ======================================================
    # LOCATION VALUES
    # ======================================================

    latitude = ""
    longitude = ""

    location_manager = None
    location_listener = None

    # ======================================================
    # SCREEN ENTER
    # ======================================================

    def on_enter(self):

        print(
            "LocationScreen entered"
        )

        self.latitude = ""
        self.longitude = ""

        self.update_location_labels()

        if ANDROID:

            self.request_location_permission()

        else:

            if "location_status" in self.ids:

                self.ids.location_status.text = (
                    "Android GPS available in APK"
                )

            print(
                "Real GPS is not available on Windows."
            )

    # ======================================================
    # GO HOME
    # ======================================================

    def go_back(self):

        try:

            if not self.manager:

                return

            if self.manager.has_screen(
                "home"
            ):

                self.stop_gps()

                self.manager.current = "home"

            else:

                print(
                    "Home screen not found"
                )

        except Exception as error:

            print(
                "Go back error:",
                error
            )

    # ======================================================
    # REQUEST LOCATION PERMISSION
    # ======================================================

    def request_location_permission(self):

        if not ANDROID:

            return

        if not ANDROID_PERMISSION_AVAILABLE:

            toast(
                "Android permission module unavailable"
            )

            return

        try:

            request_permissions(
                [
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ],
                self.permission_callback
            )

        except Exception as error:

            print(
                "Permission request error:",
                error
            )

            toast(
                "Unable to request location permission"
            )

    # ======================================================
    # PERMISSION CALLBACK
    # ======================================================

    def permission_callback(
        self,
        permissions,
        grants
    ):

        print(
            "Location permissions:",
            permissions,
            grants
        )

        try:

            if any(grants):

                Clock.schedule_once(
                    lambda dt:
                    self.start_gps(),
                    0.5
                )

            else:

                if "location_status" in self.ids:

                    self.ids.location_status.text = (
                        "Location permission denied"
                    )

                toast(
                    "Location permission is required"
                )

        except Exception as error:

            print(
                "Permission callback error:",
                error
            )

    # ======================================================
    # START GPS
    # ======================================================

    def start_gps(self):

        if not ANDROID:

            print(
                "GPS start skipped: desktop platform"
            )

            return

        if not PYJNIUS_AVAILABLE:

            toast(
                "PyJNIus is unavailable"
            )

            return

        try:

            Activity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            Context = autoclass(
                "android.content.Context"
            )

            LocationManager = autoclass(
                "android.location.LocationManager"
            )

            self.location_manager = (
                Activity.mActivity.getSystemService(
                    Context.LOCATION_SERVICE
                )
            )

            # --------------------------------------------------
            # CHECK GPS PROVIDER
            # --------------------------------------------------

            gps_enabled = (
                self.location_manager.isProviderEnabled(
                    LocationManager.GPS_PROVIDER
                )
            )

            network_enabled = (
                self.location_manager.isProviderEnabled(
                    LocationManager.NETWORK_PROVIDER
                )
            )

            if (
                not gps_enabled
                and
                not network_enabled
            ):

                if "location_status" in self.ids:

                    self.ids.location_status.text = (
                        "Please enable Location/GPS"
                    )

                toast(
                    "Turn on Location on your phone"
                )

                return

            # --------------------------------------------------
            # CREATE LISTENER
            # --------------------------------------------------

            self.location_listener = (
                AndroidLocationListener(
                    self
                )
            )

            # --------------------------------------------------
            # GPS PROVIDER
            # --------------------------------------------------

            if gps_enabled:

                self.location_manager.requestLocationUpdates(
                    LocationManager.GPS_PROVIDER,
                    1000,
                    1.0,
                    self.location_listener
                )

                print(
                    "Real GPS provider started"
                )

            # --------------------------------------------------
            # NETWORK PROVIDER
            # --------------------------------------------------

            if network_enabled:

                self.location_manager.requestLocationUpdates(
                    LocationManager.NETWORK_PROVIDER,
                    2000,
                    2.0,
                    self.location_listener
                )

                print(
                    "Network location provider started"
                )

            # --------------------------------------------------
            # LAST KNOWN LOCATION
            # --------------------------------------------------

            self.get_last_known_location(
                gps_enabled,
                network_enabled
            )

            if "location_status" in self.ids:

                self.ids.location_status.text = (
                    "Getting real location..."
                )

        except Exception as error:

            print(
                "GPS start error:",
                error
            )

            if "location_status" in self.ids:

                self.ids.location_status.text = (
                    "Unable to start GPS"
                )

            toast(
                "Unable to start GPS"
            )

    # ======================================================
    # LAST KNOWN LOCATION
    # ======================================================

    def get_last_known_location(
        self,
        gps_enabled,
        network_enabled
    ):

        try:

            LocationManager = autoclass(
                "android.location.LocationManager"
            )

            location = None

            # --------------------------------------------------
            # GPS LAST LOCATION
            # --------------------------------------------------

            if gps_enabled:

                location = (
                    self.location_manager.getLastKnownLocation(
                        LocationManager.GPS_PROVIDER
                    )
                )

            # --------------------------------------------------
            # NETWORK LAST LOCATION
            # --------------------------------------------------

            if (
                location is None
                and
                network_enabled
            ):

                location = (
                    self.location_manager.getLastKnownLocation(
                        LocationManager.NETWORK_PROVIDER
                    )
                )

            # --------------------------------------------------
            # UPDATE
            # --------------------------------------------------

            if location is not None:

                self.update_real_location(
                    location.getLatitude(),
                    location.getLongitude()
                )

        except Exception as error:

            print(
                "Last known location error:",
                error
            )

    # ======================================================
    # UPDATE REAL LOCATION
    # ======================================================

    def update_real_location(
        self,
        latitude,
        longitude
    ):

        try:

            self.latitude = (
                f"{float(latitude):.6f}"
            )

            self.longitude = (
                f"{float(longitude):.6f}"
            )

            print(
                "REAL GPS LOCATION:",
                self.latitude,
                self.longitude
            )

            Clock.schedule_once(
                lambda dt:
                self.update_location_labels(),
                0
            )

        except Exception as error:

            print(
                "Location conversion error:",
                error
            )

    # ======================================================
    # UPDATE UI
    # ======================================================

    def update_location_labels(self):

        # --------------------------------------------------
        # LATITUDE
        # --------------------------------------------------

        if "latitude" in self.ids:

            if self.latitude:

                self.ids.latitude.text = (
                    f"Latitude: {self.latitude}"
                )

            else:

                self.ids.latitude.text = (
                    "Latitude: Waiting..."
                )

        # --------------------------------------------------
        # LONGITUDE
        # --------------------------------------------------

        if "longitude" in self.ids:

            if self.longitude:

                self.ids.longitude.text = (
                    f"Longitude: {self.longitude}"
                )

            else:

                self.ids.longitude.text = (
                    "Longitude: Waiting..."
                )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        if "location_status" in self.ids:

            if (
                self.latitude
                and
                self.longitude
            ):

                self.ids.location_status.text = (
                    "✓ Real Location Available"
                )

            else:

                self.ids.location_status.text = (
                    "Getting real location..."
                )

    # ======================================================
    # REFRESH LOCATION
    # ======================================================

    def refresh_location(self):

        if not ANDROID:

            toast(
                "Real GPS works on Android APK"
            )

            return

        self.stop_gps()

        self.latitude = ""
        self.longitude = ""

        self.update_location_labels()

        Clock.schedule_once(
            lambda dt:
            self.start_gps(),
            0.5
        )

        toast(
            "Updating real location..."
        )

    # ======================================================
    # GET MAP LINK
    # ======================================================

    def get_map_link(self):

        if not self.latitude or not self.longitude:

            return None

        return (
            "https://www.google.com/maps?q="
            f"{self.latitude},{self.longitude}"
        )

    # ======================================================
    # OPEN CURRENT LOCATION
    # ======================================================

    def open_map(self):

        try:

            url = self.get_map_link()

            if not url:

                toast(
                    "Waiting for real location..."
                )

                return

            print(
                "Opening map:",
                url
            )

            webbrowser.open(
                url,
                new=2
            )

        except Exception as error:

            print(
                "Open map error:",
                error
            )

            toast(
                "Unable to open map"
            )

    # ======================================================
    # NEARBY POLICE
    # ======================================================

    def nearby_police(self):

        if not self.latitude or not self.longitude:

            toast(
                "Waiting for real location..."
            )

            return False

        try:

            url = (
                "https://www.google.com/maps/"
                "search/police+station/"
                f"@{self.latitude},"
                f"{self.longitude},15z"
            )

            print(
                "Police map:",
                url
            )

            webbrowser.open(
                url,
                new=2
            )

            toast(
                "Opening nearby police stations"
            )

            return True

        except Exception as error:

            print(
                "Nearby police error:",
                error
            )

            toast(
                "Unable to open nearby police"
            )

            return False

    # ======================================================
    # NEARBY HOSPITAL
    # ======================================================

    def nearby_hospital(self):

        if not self.latitude or not self.longitude:

            toast(
                "Waiting for real location..."
            )

            return False

        try:

            url = (
                "https://www.google.com/maps/"
                "search/hospital/"
                f"@{self.latitude},"
                f"{self.longitude},15z"
            )

            print(
                "Hospital map:",
                url
            )

            webbrowser.open(
                url,
                new=2
            )

            toast(
                "Opening nearby hospitals"
            )

            return True

        except Exception as error:

            print(
                "Nearby hospital error:",
                error
            )

            toast(
                "Unable to open nearby hospitals"
            )

            return False

    # ======================================================
    # SAFE ROUTE
    # ======================================================

    def go_home(self):

        if not self.latitude or not self.longitude:

            toast(
                "Current location is not available"
            )

            return False

        try:

            # --------------------------------------------------
            # IMPORTANT
            #
            # Replace these with the saved safe-location
            # coordinates when you implement Safe Location.
            # --------------------------------------------------

            home_lat = "11.0168"
            home_lon = "76.9558"

            url = (
                "https://www.google.com/maps/dir/"
                f"{self.latitude},{self.longitude}/"
                f"{home_lat},{home_lon}"
            )

            print(
                "Safe route:",
                url
            )

            webbrowser.open(
                url,
                new=2
            )

            toast(
                "Opening safe route"
            )

            return True

        except Exception as error:

            print(
                "Safe route error:",
                error
            )

            toast(
                "Unable to open safe route"
            )

            return False

    # ======================================================
    # STOP GPS
    # ======================================================

    def stop_gps(self):

        try:

            if (
                self.location_manager
                and
                self.location_listener
            ):

                self.location_manager.removeUpdates(
                    self.location_listener
                )

                print(
                    "GPS updates stopped"
                )

        except Exception as error:

            print(
                "GPS stop error:",
                error
            )

        finally:

            self.location_listener = None

    # ======================================================
    # SCREEN LEAVE
    # ======================================================

    def on_leave(self):

        self.stop_gps()