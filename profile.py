import os
import shutil

from kivy.properties import StringProperty
from kivy.utils import platform

from kivymd.toast import toast
from kivymd.uix.screen import MDScreen

from modules.session import SessionManager


class ProfileScreen(MDScreen):

    first_name = StringProperty("")
    last_name = StringProperty("")

    email = StringProperty("")
    phone = StringProperty("")

    blood_group = StringProperty("")
    gender = StringProperty("")
    address = StringProperty("")

    user_photo = StringProperty("")

    # ==================================================
    # LOAD PROFILE
    # ==================================================

    def on_enter(self):
        self.load_profile()

    def load_profile(self):

        data = SessionManager.load()

        self.first_name = data.get(
            "first_name", ""
        )

        self.last_name = data.get(
            "last_name", ""
        )

        self.email = data.get(
            "email", ""
        )

        self.phone = data.get(
            "phone", ""
        )

        self.blood_group = data.get(
            "blood_group", ""
        )

        self.gender = data.get(
            "gender", ""
        )

        self.address = data.get(
            "address", ""
        )

        self.user_photo = data.get(
            "profile_photo", ""
        )

        self.refresh_profile_photo()

    # ==================================================
    # REFRESH PHOTO
    # ==================================================

    def refresh_profile_photo(self):

        if "profile_image" not in self.ids:
            return

        if (
            self.user_photo
            and os.path.exists(
                self.user_photo
            )
        ):
            self.ids.profile_image.source = (
                self.user_photo
            )
        else:
            self.ids.profile_image.source = (
                "assets/profile.png"
            )

        try:
            self.ids.profile_image.reload()
        except Exception:
            pass

    # ==================================================
    # GENDER DROPDOWN
    # ==================================================

    def open_gender_menu(self):
        from kivymd.uix.menu import MDDropdownMenu
        from kivy.metrics import dp

        if getattr(self, "_gender_menu", None):
            self._gender_menu.dismiss()

        items = [
            {"text": "Male", "viewclass": "OneLineListItem", "height": dp(48),
             "on_release": lambda value="Male": self.select_gender(value)},
            {"text": "Female", "viewclass": "OneLineListItem", "height": dp(48),
             "on_release": lambda value="Female": self.select_gender(value)},
        ]

        self._gender_menu = MDDropdownMenu(
            caller=self.ids.gender_field,
            items=items,
            width_mult=4,
        )
        self._gender_menu.open()

    def select_gender(self, value):
        self.gender = value
        if "gender_field" in self.ids:
            self.ids.gender_field.text = value
        if getattr(self, "_gender_menu", None):
            self._gender_menu.dismiss()

    # ==================================================
    # GALLERY
    # ==================================================

    def choose_from_gallery(self):

        if platform == "android":
            self.choose_android_image()
        else:
            self.choose_desktop_image()

    # --------------------------------------------------
    # Android gallery
    # --------------------------------------------------

    def choose_android_image(self):

        try:

            from plyer import filechooser

            filechooser.open_file(
                on_selection=self.gallery_selected
            )

        except Exception as e:

            print(
                "Android gallery error:",
                e
            )

            toast(
                "Unable to open gallery"
            )

    # --------------------------------------------------
    # Desktop gallery/file picker
    # --------------------------------------------------

    def choose_desktop_image(self):

        try:

            from tkinter import Tk
            from tkinter.filedialog import askopenfilename

            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            path = askopenfilename(
                title="Select Profile Photo",
                filetypes=[
                    (
                        "Image Files",
                        "*.png *.jpg *.jpeg *.webp"
                    )
                ]
            )

            root.destroy()

            if path:
                self.gallery_selected(
                    [path]
                )

        except Exception as e:

            print(
                "Desktop gallery error:",
                e
            )

            toast(
                "Unable to open image picker"
            )

    # ==================================================
    # GALLERY CALLBACK
    # ==================================================

    def gallery_selected(self, selection):

        if not selection:
            return

        if isinstance(
            selection,
            (list, tuple)
        ):
            source = selection[0]
        else:
            source = selection

        if not source:
            return

        self.set_profile_photo(
            str(source)
        )

    # ==================================================
    # CAMERA
    # ==================================================

    def capture_profile_photo(self):

        if platform == "android":

            self.capture_android_photo()

        else:

            self.capture_desktop_photo()

    # --------------------------------------------------
    # Android camera
    # --------------------------------------------------

    def capture_android_photo(self):

        try:

            from plyer import camera

            output_path = (
                SessionManager
                .get_profile_photo_path()
            )

            camera.take_picture(
                filename=output_path,
                on_complete=self.camera_completed
            )

            toast(
                "Opening camera..."
            )

        except Exception as e:

            print(
                "Android camera error:",
                e
            )

            toast(
                "Unable to open camera"
            )

    # --------------------------------------------------
    # Android camera callback
    # --------------------------------------------------

    def camera_completed(self, path):

        if path:
            self.set_profile_photo(
                str(path)
            )

    # --------------------------------------------------
    # Desktop camera
    # --------------------------------------------------

    def capture_desktop_photo(self):

        try:

            import cv2

        except ImportError:

            toast(
                "OpenCV is not installed"
            )

            return

        try:

            camera = cv2.VideoCapture(0)

            if not camera.isOpened():

                toast(
                    "Camera not found"
                )

                return

            toast(
                "SPACE = Capture   ESC = Cancel"
            )

            while True:

                success, frame = camera.read()

                if not success:
                    break

                cv2.imshow(
                    "Safivox Profile Camera",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if key == 32:

                    output_path = (
                        SessionManager
                        .get_profile_photo_path()
                    )

                    cv2.imwrite(
                        output_path,
                        frame
                    )

                    camera.release()
                    cv2.destroyAllWindows()

                    self.set_profile_photo(
                        output_path
                    )

                    return

                if key == 27:

                    camera.release()
                    cv2.destroyAllWindows()

                    toast(
                        "Camera cancelled"
                    )

                    return

            camera.release()
            cv2.destroyAllWindows()

        except Exception as e:

            print(
                "Desktop camera error:",
                e
            )

            toast(
                "Unable to capture photo"
            )

    # ==================================================
    # SET PHOTO
    # ==================================================

    def set_profile_photo(self, source_path):

        if not source_path:
            return

        source_path = str(
            source_path
        )

        if not os.path.exists(source_path):

            toast(
                "Selected image not found"
            )

            return

        try:

            destination = (
                SessionManager
                .get_profile_photo_path()
            )

            # Don't copy the same file over itself.
            if (
                os.path.abspath(
                    source_path
                )
                !=
                os.path.abspath(
                    destination
                )
            ):

                shutil.copy2(
                    source_path,
                    destination
                )

            self.user_photo = destination

            # Save path in session.
            SessionManager.update_profile(
                profile_photo=destination
            )

            self.refresh_profile_photo()

            self.update_home_photo()

            toast(
                "Profile photo updated"
            )

        except Exception as e:

            print(
                "Profile photo save error:",
                e
            )

            toast(
                "Unable to save profile photo"
            )

    # ==================================================
    # CHANGE PROFILE PHOTO
    # ==================================================

    def change_profile_photo(self):

        self.choose_from_gallery()

    # ==================================================
    # DELETE PROFILE PHOTO
    # ==================================================

    def delete_profile_photo(self):

        try:

            photo = self.user_photo

            if (
                photo
                and os.path.exists(photo)
            ):

                os.remove(photo)

            self.user_photo = ""

            SessionManager.update_profile(
                profile_photo=""
            )

            self.refresh_profile_photo()

            self.update_home_photo()

            toast(
                "Profile photo deleted"
            )

        except Exception as e:

            print(
                "Delete profile photo error:",
                e
            )

            toast(
                "Unable to delete photo"
            )

    # ==================================================
    # UPDATE HOME PHOTO
    # ==================================================

    def update_home_photo(self):

        if not self.manager:
            return

        if not self.manager.has_screen(
            "home"
        ):
            return

        home = self.manager.get_screen(
            "home"
        )

        home.set_user_info(
            photo=self.user_photo
        )

    # ==================================================
    # SAVE PROFILE
    # ==================================================

    def save_profile(self):

        first_name = (
            self.ids.first_name.text.strip()
        )

        last_name = (
            self.ids.last_name.text.strip()
        )

        email = (
            self.ids.email.text.strip()
        )

        phone = (
            self.ids.phone.text.strip()
        )

        blood_group = (
            self.ids.blood_group.text.strip()
        )

        gender = self.ids.gender_field.text.strip()

        address = (
            self.ids.address.text.strip()
        )

        if not first_name:

            toast(
                "Enter first name"
            )

            return

        if not email:

            toast(
                "Enter email address"
            )

            return

        if "@" not in email:

            toast(
                "Enter a valid email address"
            )

            return

        if not phone:

            toast(
                "Enter phone number"
            )

            return

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.blood_group = blood_group
        self.gender = gender
        self.address = address

        success = SessionManager.update_profile(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            blood_group=blood_group,
            gender=gender,
            address=address,
            profile_photo=self.user_photo
        )

        if not success:

            toast(
                "Unable to save profile"
            )

            return

        self.update_home_profile()

        toast(
            "Profile saved successfully"
        )

    # ==================================================
    # UPDATE HOME PROFILE
    # ==================================================

    def update_home_profile(self):

        if not self.manager:
            return

        if not self.manager.has_screen(
            "home"
        ):
            return

        home = self.manager.get_screen(
            "home"
        )

        full_name = (
            f"{self.first_name} "
            f"{self.last_name}"
        ).strip()

        home.set_user_info(
            name=(
                full_name
                if full_name
                else self.first_name
            ),
            email=self.email,
            photo=self.user_photo
        )


    # ==================================================
    # CLEAR PROFILE
    # ==================================================

    def clear_profile(self):
        self.first_name = ""
        self.last_name = ""
        self.email = ""
        self.phone = ""
        self.gender = ""
        self.blood_group = ""
        self.address = ""

        if self.user_photo and os.path.exists(self.user_photo):
            try:
                os.remove(self.user_photo)
            except Exception:
                pass
        self.user_photo = ""

        SessionManager.update_profile(
            first_name="", last_name="", email="", phone="",
            gender="", blood_group="", address="", profile_photo=""
        )

        for field_id in ("first_name", "last_name", "email", "phone", "gender_field", "blood_group", "address"):
            if field_id in self.ids:
                self.ids[field_id].text = ""

        self.refresh_profile_photo()
        self.update_home_profile()
        toast("Profile cleared")

    # ==================================================
    # BACK
    # ==================================================

    def go_back(self):

        if self.manager:

            self.manager.current = "home"