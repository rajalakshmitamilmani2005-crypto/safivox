import os
import json
import re
import shutil

from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField

from modules.android_call import AndroidCall


# ==========================================================
# OPTIONAL ANDROID / DEVICE IMPORTS
# ==========================================================

try:
    from plyer import camera
except Exception:
    camera = None

try:
    from plyer import filechooser
except Exception:
    filechooser = None


# ==========================================================
# PATHS
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

CONTACT_FILE = os.path.join(
    DATA_DIR,
    "emergency_contacts.json"
)

CONTACT_PHOTO_DIR = os.path.join(
    DATA_DIR,
    "contact_photos"
)

DEFAULT_PROFILE_IMAGE = os.path.join(
    BASE_DIR,
    "assets",
    "profile.png"
)


# ==========================================================
# CONTACT SCREEN
# ==========================================================

class ContactsScreen(MDScreen):

    contacts = ListProperty([])

    search_text = StringProperty("")

    # Used when taking/selecting a photo
    photo_callback = None

    # Current contact being edited
    editing_contact = None

    # ======================================================
    # SCREEN ENTER
    # ======================================================

    def on_enter(self):

        self.load_contacts()

        Clock.schedule_once(
            self.refresh_contact_list,
            0.1
        )

    # ======================================================
    # DATA DIRECTORY
    # ======================================================

    def ensure_data_directory(self):

        os.makedirs(
            DATA_DIR,
            exist_ok=True
        )

        os.makedirs(
            CONTACT_PHOTO_DIR,
            exist_ok=True
        )

    # ======================================================
    # LOAD CONTACTS
    # ======================================================

    def load_contacts(self):

        self.ensure_data_directory()

        if not os.path.exists(CONTACT_FILE):

            self.contacts = []

            self.save_contacts()

            return

        try:

            with open(
                CONTACT_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if isinstance(data, list):

                self.contacts = data

            else:

                self.contacts = []

        except Exception as error:

            print(
                "Error loading contacts:",
                error
            )

            self.contacts = []

    # ======================================================
    # SAVE CONTACTS
    # ======================================================

    def save_contacts(self):

        self.ensure_data_directory()

        try:

            with open(
                CONTACT_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.contacts,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except Exception as error:

            print(
                "Error saving contacts:",
                error
            )

            return False

    # ======================================================
    # REFRESH CONTACT LIST
    #
    # IMPORTANT:
    # *args prevents:
    # refresh_contact_list() takes 1 positional argument
    # but 2 were given
    # ======================================================

    def refresh_contact_list(self, *args):

        if "contact_list" not in self.ids:
            return

        contact_list = self.ids.contact_list

        contact_list.clear_widgets()

        search = (
            self.search_text
            .strip()
            .lower()
        )

        filtered_contacts = []

        for contact in self.contacts:

            name = str(
                contact.get(
                    "name",
                    ""
                )
            )

            phone = str(
                contact.get(
                    "phone",
                    ""
                )
            )

            if (
                not search
                or search in name.lower()
                or search in phone.lower()
            ):

                filtered_contacts.append(
                    contact
                )

        # ==================================================
        # COUNT
        # ==================================================

        count = len(
            filtered_contacts
        )

        if "contact_count" in self.ids:

            if count == 1:

                self.ids.contact_count.text = (
                    "1 emergency contact"
                )

            else:

                self.ids.contact_count.text = (
                    f"{count} emergency contacts"
                )

        # ==================================================
        # EMPTY LIST
        # ==================================================

        if not filtered_contacts:

            empty = Label(
                text=(
                    "No emergency contacts found.\n\n"
                    "Tap + ADD CONTACT to add one."
                ),
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=120,
                color=(
                    0.35,
                    0.35,
                    0.40,
                    1
                )
            )

            empty.bind(
                size=lambda instance, value:
                setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            contact_list.add_widget(
                empty
            )

            return

        # ==================================================
        # CONTACT ROWS
        # ==================================================

        for index, contact in enumerate(
            filtered_contacts
        ):

            self.add_contact_widget(
                contact,
                index
            )

    # ======================================================
    # CREATE CONTACT ROW
    # ======================================================

    def add_contact_widget(
        self,
        contact,
        index
    ):

        name = str(
            contact.get(
                "name",
                "Unknown"
            )
        )

        phone = str(
            contact.get(
                "phone",
                ""
            )
        )

        photo = str(
            contact.get(
                "photo",
                ""
            )
        )

        # Make sure invalid photo paths don't get passed
        if not photo or not os.path.exists(photo):

            photo = ""

        card = ContactRow(
            contact_name=name,
            contact_phone=phone,
            contact_photo=photo
        )

        card.contact_index = index

        card.call_callback = (
            self.call_contact
        )

        card.delete_callback = (
            self.delete_contact
        )

        card.edit_callback = (
            self.edit_contact
        )

        self.ids.contact_list.add_widget(
            card
        )

    # ======================================================
    # SEARCH
    # ======================================================

    def search_contact(
        self,
        text
    ):

        self.search_text = (
            text or ""
        )

        self.refresh_contact_list()

    # ======================================================
    # ADD CONTACT
    # ======================================================

    def add_contact(self):

        self.editing_contact = None

        self._open_contact_dialog(
            title="Add Emergency Contact",
            contact=None
        )

    # ======================================================
    # EDIT CONTACT
    # ======================================================

    def edit_contact(
        self,
        index
    ):

        if index < 0:
            return

        if index >= len(self.contacts):
            toast("Contact not found")
            return

        self.editing_contact = index

        contact = self.contacts[index]

        self._open_contact_dialog(
            title="Edit Emergency Contact",
            contact=contact
        )

    # ======================================================
    # CONTACT DIALOG
    # ======================================================

    def _open_contact_dialog(
        self,
        title,
        contact=None
    ):

        old_name = ""

        old_phone = ""

        old_photo = ""

        if contact:

            old_name = str(
                contact.get(
                    "name",
                    ""
                )
            )

            old_phone = str(
                contact.get(
                    "phone",
                    ""
                )
            )

            old_photo = str(
                contact.get(
                    "photo",
                    ""
                )
            )

        # --------------------------------------------------
        # NAME
        # --------------------------------------------------

        name_field = MDTextField(
            hint_text="Contact name",
            mode="rectangle",
            multiline=False,
            text=old_name
        )

        # --------------------------------------------------
        # PHONE
        # --------------------------------------------------

        phone_field = MDTextField(
            hint_text="Phone number",
            mode="rectangle",
            multiline=False,
            input_type="tel",
            text=old_phone
        )

        # --------------------------------------------------
        # PHOTO STATUS
        # --------------------------------------------------

        photo_label = Label(
            text=(
                "Profile photo selected"
                if old_photo
                and os.path.exists(old_photo)
                else
                "No profile photo selected"
            ),
            size_hint_y=None,
            height=35,
            color=(
                0.25,
                0.25,
                0.30,
                1
            )
        )

        # --------------------------------------------------
        # PHOTO BUTTONS
        # --------------------------------------------------

        photo_buttons = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=48
        )

        gallery_button = MDRaisedButton(
            text="GALLERY",
            size_hint_x=0.5
        )

        camera_button = MDRaisedButton(
            text="CAMERA",
            size_hint_x=0.5
        )

        photo_buttons.add_widget(
            gallery_button
        )

        photo_buttons.add_widget(
            camera_button
        )

        # --------------------------------------------------
        # CONTENT
        # --------------------------------------------------

        content = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10,
            size_hint_y=None,
            height=250
        )

        content.add_widget(
            name_field
        )

        content.add_widget(
            phone_field
        )

        content.add_widget(
            photo_label
        )

        content.add_widget(
            photo_buttons
        )

        # --------------------------------------------------
        # DIALOG
        # --------------------------------------------------

        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x:
                    dialog.dismiss()
                ),

                MDRaisedButton(
                    text=(
                        "UPDATE CONTACT"
                        if contact
                        else
                        "ADD CONTACT"
                    ),
                    on_release=lambda x:
                    self.save_contact_from_dialog(
                        dialog,
                        name_field,
                        phone_field,
                        photo_label,
                        contact
                    )
                )
            ]
        )

        # --------------------------------------------------
        # GALLERY CALLBACK
        # --------------------------------------------------

        gallery_button.bind(
            on_release=lambda x:
            self.select_gallery_photo(
                photo_label
            )
        )

        # --------------------------------------------------
        # CAMERA CALLBACK
        # --------------------------------------------------

        camera_button.bind(
            on_release=lambda x:
            self.take_contact_photo(
                photo_label
            )
        )

        dialog.open()

    # ======================================================
    # GALLERY
    # ======================================================

    def select_gallery_photo(
        self,
        photo_label
    ):

        if filechooser is None:

            toast(
                "Gallery is not available"
            )

            return

        self.photo_callback = (
            photo_label
        )

        try:

            filechooser.open_file(
                on_selection=self.gallery_selected
            )

        except Exception as error:

            print(
                "Gallery error:",
                error
            )

            toast(
                "Unable to open gallery"
            )

    # ======================================================
    # GALLERY RESULT
    # ======================================================

    def gallery_selected(
        self,
        selection
    ):

        if not selection:
            return

        try:

            source = selection[0]

            saved_photo = (
                self.copy_contact_photo(
                    source
                )
            )

            if saved_photo:

                if self.photo_callback:

                    self.photo_callback.text = (
                        "Profile photo selected"
                    )

                    self.photo_callback.color = (
                        0.08,
                        0.67,
                        0.38,
                        1
                    )

                self._pending_photo = (
                    saved_photo
                )

                toast(
                    "Profile photo selected"
                )

        except Exception as error:

            print(
                "Gallery selection error:",
                error
            )

            toast(
                "Could not select photo"
            )

    # ======================================================
    # CAMERA
    # ======================================================

    def take_contact_photo(
        self,
        photo_label
    ):

        if camera is None:

            toast(
                "Camera is not available on this device"
            )

            return

        self.photo_callback = (
            photo_label
        )

        self.ensure_data_directory()

        photo_path = os.path.join(
            CONTACT_PHOTO_DIR,
            "contact_camera.jpg"
        )

        try:

            camera.take_picture(
                filename=photo_path,
                on_complete=self.camera_completed
            )

            toast(
                "Opening camera..."
            )

        except Exception as error:

            print(
                "Camera error:",
                error
            )

            toast(
                "Unable to open camera"
            )

    # ======================================================
    # CAMERA RESULT
    # ======================================================

    def camera_completed(
        self,
        photo_path
    ):

        if not photo_path:

            toast(
                "Photo was not captured"
            )

            return

        if not os.path.exists(
            photo_path
        ):

            toast(
                "Captured photo not found"
            )

            return

        try:

            saved_photo = (
                self.copy_contact_photo(
                    photo_path
                )
            )

            if saved_photo:

                if self.photo_callback:

                    self.photo_callback.text = (
                        "Profile photo selected"
                    )

                    self.photo_callback.color = (
                        0.08,
                        0.67,
                        0.38,
                        1
                    )

                self._pending_photo = (
                    saved_photo
                )

                toast(
                    "Profile photo captured"
                )

        except Exception as error:

            print(
                "Camera processing error:",
                error
            )

            toast(
                "Could not save photo"
            )

    # ======================================================
    # COPY PHOTO
    # ======================================================

    def copy_contact_photo(
        self,
        source
    ):

        self.ensure_data_directory()

        if not source:
            return ""

        if not os.path.exists(
            source
        ):

            print(
                "Photo source not found:",
                source
            )

            return ""

        try:

            import time

            filename = (
                f"contact_"
                f"{int(time.time() * 1000)}.jpg"
            )

            destination = os.path.join(
                CONTACT_PHOTO_DIR,
                filename
            )

            shutil.copy2(
                source,
                destination
            )

            return destination

        except Exception as error:

            print(
                "Photo copy error:",
                error
            )

            return ""

    # ======================================================
    # SAVE CONTACT FROM DIALOG
    # ======================================================

    def save_contact_from_dialog(
        self,
        dialog,
        name_field,
        phone_field,
        photo_label,
        old_contact=None
    ):

        name = (
            name_field.text
            .strip()
        )

        phone = (
            phone_field.text
            .strip()
        )

        # --------------------------------------------------
        # VALIDATE NAME
        # --------------------------------------------------

        if not name:

            toast(
                "Please enter contact name"
            )

            return

        # --------------------------------------------------
        # VALIDATE PHONE
        # --------------------------------------------------

        if not phone:

            toast(
                "Please enter phone number"
            )

            return

        clean_phone = (
            self.clean_phone_number(
                phone
            )
        )

        if not clean_phone:

            toast(
                "Enter a valid phone number"
            )

            return

        # --------------------------------------------------
        # DUPLICATE CHECK
        # --------------------------------------------------

        editing_index = (
            self.editing_contact
        )

        for index, contact in enumerate(
            self.contacts
        ):

            if (
                editing_index is not None
                and
                index == editing_index
            ):
                continue

            existing_phone = (
                self.clean_phone_number(
                    contact.get(
                        "phone",
                        ""
                    )
                )
            )

            if existing_phone == clean_phone:

                toast(
                    "This phone number already exists"
                )

                return

        # --------------------------------------------------
        # PHOTO
        # --------------------------------------------------

        new_photo = ""

        if hasattr(
            self,
            "_pending_photo"
        ):

            new_photo = (
                self._pending_photo
            )

        # If editing and no new photo was selected,
        # keep the old photo.

        if (
            not new_photo
            and
            old_contact
        ):

            new_photo = str(
                old_contact.get(
                    "photo",
                    ""
                )
            )

        # --------------------------------------------------
        # CREATE / UPDATE
        # --------------------------------------------------

        new_contact = {
            "name": name,
            "phone": clean_phone,
            "photo": new_photo
        }

        # --------------------------------------------------
        # UPDATE
        # --------------------------------------------------

        if (
            editing_index is not None
            and
            editing_index >= 0
            and
            editing_index < len(
                self.contacts
            )
        ):

            self.contacts[
                editing_index
            ] = new_contact

            message = (
                f"{name} updated successfully"
            )

        # --------------------------------------------------
        # ADD
        # --------------------------------------------------

        else:

            self.contacts.append(
                new_contact
            )

            message = (
                f"{name} added successfully"
            )

        # --------------------------------------------------
        # SAVE
        # --------------------------------------------------

        if self.save_contacts():

            dialog.dismiss()

            self.editing_contact = None

            self._pending_photo = ""

            self.refresh_contact_list()

            toast(
                message
            )

        else:

            toast(
                "Could not save contact"
            )

    # ======================================================
    # CLEAN PHONE NUMBER
    # ======================================================

    def clean_phone_number(
        self,
        phone
    ):

        if not phone:

            return ""

        phone = str(
            phone
        ).strip()

        phone = re.sub(
            r"[^\d+]",
            "",
            phone
        )

        if "+" in phone:

            phone = (
                "+"
                + phone.replace(
                    "+",
                    ""
                )
            )

        return phone

    # ======================================================
    # CALL CONTACT
    # ======================================================

    def call_contact(
        self,
        name,
        phone
    ):

        if not phone:

            toast(
                "Phone number is not available"
            )

            return

        try:

            success = (
                AndroidCall.make_call(
                    phone
                )
            )

        except Exception as error:

            print(
                "Call error:",
                error
            )

            success = False

        if success:

            toast(
                f"Calling {name}"
            )

        else:

            toast(
                "Phone calling is available on Android"
            )

    # ======================================================
    # DELETE CONTACT
    # ======================================================

    def delete_contact(
        self,
        name,
        phone
    ):

        found = False

        contact_to_delete = None

        for contact in list(
            self.contacts
        ):

            if (
                contact.get("name")
                == name
                and
                contact.get("phone")
                == phone
            ):

                contact_to_delete = contact

                self.contacts.remove(
                    contact
                )

                found = True

                break

        if not found:

            toast(
                "Contact not found"
            )

            return

        # --------------------------------------------------
        # DELETE PHOTO
        # --------------------------------------------------

        if contact_to_delete:

            photo = contact_to_delete.get(
                "photo",
                ""
            )

            if (
                photo
                and
                os.path.exists(photo)
            ):

                try:

                    os.remove(photo)

                except Exception as error:

                    print(
                        "Photo delete error:",
                        error
                    )

        # --------------------------------------------------
        # SAVE
        # --------------------------------------------------

        if self.save_contacts():

            self.refresh_contact_list()

            toast(
                f"{name} deleted"
            )

        else:

            toast(
                "Could not delete contact"
            )

    # ======================================================
    # BACK
    # ======================================================

    def go_back(self):

        if not self.manager:

            return

        if self.manager.has_screen(
            "home"
        ):

            self.manager.current = (
                "home"
            )


# ==========================================================
# CONTACT ROW
# ==========================================================

class ContactRow(BoxLayout):

    contact_name = StringProperty("")

    contact_phone = StringProperty("")

    contact_photo = StringProperty("")

    contact_index = -1

    call_callback = None

    delete_callback = None

    edit_callback = None

    # ======================================================
    # CALL
    # ======================================================

    def call_pressed(self):

        if self.call_callback:

            self.call_callback(
                self.contact_name,
                self.contact_phone
            )

    # ======================================================
    # EDIT
    # ======================================================

    def edit_pressed(self):

        if self.edit_callback:

            self.edit_callback(
                self.contact_index
            )

    # ======================================================
    # DELETE
    # ======================================================

    def delete_pressed(self):

        if self.delete_callback:

            self.delete_callback(
                self.contact_name,
                self.contact_phone
            )