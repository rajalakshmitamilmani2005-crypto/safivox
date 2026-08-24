import os
import threading
from datetime import datetime

from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.utils import platform

from kivymd.toast import toast
from kivymd.uix.screen import MDScreen


class EvidenceScreen(MDScreen):
    """
    Safivox Evidence Manager

    Windows:
        Saves to:
        <project>/evidence/photos
        <project>/evidence/videos
        <project>/evidence/audio

    Android:
        Saves to the app evidence directory and
        exports media to Android shared media:
            Pictures/Safivox
            Movies/Safivox
            Music/Safivox
    """

    # ==========================================================
    # UI PROPERTIES
    # ==========================================================

    status_text = StringProperty(
        "Evidence is ready"
    )

    photo_count = NumericProperty(0)
    video_count = NumericProperty(0)
    audio_count = NumericProperty(0)

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # ------------------------------------------------------
        # Determine project directory
        # ------------------------------------------------------

        self.project_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        # ------------------------------------------------------
        # PRIVATE / PROJECT EVIDENCE DIRECTORY
        # ------------------------------------------------------

        if platform == "android":

            try:

                from kivy.app import App

                app = App.get_running_app()

                if app:

                    self.storage_root = app.user_data_dir

                else:

                    self.storage_root = self.project_dir

            except Exception:

                self.storage_root = self.project_dir

        else:

            # On Windows:
            # save directly inside project folder.
            self.storage_root = self.project_dir

        self.base_dir = os.path.join(
            self.storage_root,
            "evidence"
        )

        self.photo_dir = os.path.join(
            self.base_dir,
            "photos"
        )

        self.video_dir = os.path.join(
            self.base_dir,
            "videos"
        )

        self.audio_dir = os.path.join(
            self.base_dir,
            "audio"
        )

        self.ensure_directories()

        self.refresh_counts()

        print(
            "Evidence root:",
            self.base_dir
        )

    # ==========================================================
    # CREATE DIRECTORIES
    # ==========================================================

    def ensure_directories(self):

        os.makedirs(
            self.photo_dir,
            exist_ok=True
        )

        os.makedirs(
            self.video_dir,
            exist_ok=True
        )

        os.makedirs(
            self.audio_dir,
            exist_ok=True
        )

    # ==========================================================
    # SCREEN ENTER
    # ==========================================================

    def on_enter(self):

        self.ensure_directories()

        self.refresh_counts()

        print(
            "Photo folder:",
            self.photo_dir
        )

        print(
            "Video folder:",
            self.video_dir
        )

        print(
            "Audio folder:",
            self.audio_dir
        )

    # ==========================================================
    # CREATE UNIQUE FILE NAME
    # ==========================================================

    def create_filename(
        self,
        prefix,
        extension
    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        return (
            f"{prefix}_{timestamp}{extension}"
        )

    # ==========================================================
    # GET FILES
    # ==========================================================

    def get_files(
        self,
        directory,
        extensions=None
    ):

        if not os.path.isdir(
            directory
        ):

            return []

        files = []

        for filename in os.listdir(
            directory
        ):

            path = os.path.join(
                directory,
                filename
            )

            if not os.path.isfile(
                path
            ):

                continue

            if extensions:

                if not any(
                    filename.lower().endswith(ext)
                    for ext in extensions
                ):

                    continue

            files.append(
                path
            )

        files.sort(
            key=lambda item:
                os.path.getmtime(item),
            reverse=True
        )

        return files

    # ==========================================================
    # COUNTS
    # ==========================================================

    def refresh_counts(self):

        self.photo_count = len(
            self.get_files(
                self.photo_dir,
                [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp"
                ]
            )
        )

        self.video_count = len(
            self.get_files(
                self.video_dir,
                [
                    ".mp4",
                    ".avi",
                    ".mov",
                    ".mkv"
                ]
            )
        )

        self.audio_count = len(
            self.get_files(
                self.audio_dir,
                [
                    ".wav",
                    ".mp3",
                    ".m4a",
                    ".aac"
                ]
            )
        )

    # ==========================================================
    # TAKE PHOTO
    # ==========================================================

    def take_photo(self):

        self.ensure_directories()

        output_path = os.path.join(
            self.photo_dir,
            self.create_filename(
                "photo",
                ".jpg"
            )
        )

        print(
            "Photo output:",
            output_path
        )

        # ======================================================
        # ANDROID
        # ======================================================

        if platform == "android":

            try:

                from plyer import camera

                camera.take_picture(
                    filename=output_path,
                    on_complete=self.photo_completed
                )

                self.status_text = (
                    "Opening camera..."
                )

                return output_path

            except Exception as e:

                print(
                    "Android camera error:",
                    e
                )

                self.status_text = (
                    "Camera unavailable"
                )

                toast(
                    "Unable to open camera"
                )

                return None

        # ======================================================
        # WINDOWS
        # ======================================================

        self.capture_desktop_photo(
            output_path
        )

        return output_path

    # ==========================================================
    # ANDROID PHOTO CALLBACK
    # ==========================================================

    def photo_completed(
        self,
        path
    ):

        if not path:

            return

        path = str(path)

        if not os.path.isfile(path):

            print(
                "Captured photo not found:",
                path
            )

            self.status_text = (
                "Photo capture failed"
            )

            return

        self.finish_photo(
            path
        )

    # ==========================================================
    # DESKTOP PHOTO
    # ==========================================================

    def capture_desktop_photo(
        self,
        output_path
    ):

        try:

            import cv2

        except ImportError:

            print(
                "OpenCV is not installed"
            )

            self.status_text = (
                "OpenCV is not installed"
            )

            toast(
                "Install OpenCV for camera support"
            )

            return

        camera = None

        try:

            camera = cv2.VideoCapture(0)

            if not camera.isOpened():

                self.status_text = (
                    "Camera not found"
                )

                toast(
                    "Camera not found"
                )

                return

            print(
                "Press SPACE to capture"
            )

            print(
                "Press ESC to cancel"
            )

            while True:

                success, frame = (
                    camera.read()
                )

                if not success:

                    break

                cv2.imshow(
                    "Safivox - Capture Photo",
                    frame
                )

                key = (
                    cv2.waitKey(1)
                    &
                    0xFF
                )

                # SPACE
                if key == 32:

                    saved = cv2.imwrite(
                        output_path,
                        frame
                    )

                    if saved:

                        print(
                            "Photo saved:",
                            output_path
                        )

                        self.finish_photo(
                            output_path
                        )

                    else:

                        print(
                            "Photo save failed"
                        )

                    break

                # ESC
                if key == 27:

                    print(
                        "Photo capture cancelled"
                    )

                    self.status_text = (
                        "Photo capture cancelled"
                    )

                    break

        except Exception as e:

            print(
                "Desktop photo error:",
                e
            )

            self.status_text = (
                "Photo capture failed"
            )

        finally:

            try:

                if camera:

                    camera.release()

            except Exception:

                pass

            try:

                cv2.destroyAllWindows()

            except Exception:

                pass

    # ==========================================================
    # FINISH PHOTO
    # ==========================================================

    def finish_photo(
        self,
        path
    ):

        if not os.path.isfile(path):

            print(
                "Photo does not exist:",
                path
            )

            return

        self.refresh_counts()

        self.status_text = (
            "Photo saved successfully"
        )

        print(
            "PHOTO SAVED:",
            path
        )

        # Android shared gallery
        if platform == "android":

            self.export_to_android_media(
                path,
                "image"
            )

        toast(
            "Photo saved successfully"
        )

    # ==========================================================
    # RECORD VIDEO
    # ==========================================================

    def record_video(self):

        self.ensure_directories()

        output_path = os.path.join(
            self.video_dir,
            self.create_filename(
                "video",
                ".mp4"
            )
        )

        print(
            "Video output:",
            output_path
        )

        # ------------------------------------------------------
        # Android
        # ------------------------------------------------------

        if platform == "android":

            toast(
                "Android video capture requires the Android camera module"
            )

            self.status_text = (
                "Android video camera not connected"
            )

            return None

        # ------------------------------------------------------
        # Windows
        # ------------------------------------------------------

        return self.capture_desktop_video(
            output_path
        )

    # ==========================================================
    # DESKTOP VIDEO
    # ==========================================================

    def capture_desktop_video(
        self,
        output_path
    ):

        try:

            import cv2

        except ImportError:

            toast(
                "Install OpenCV first"
            )

            return None

        camera = None
        writer = None

        try:

            camera = cv2.VideoCapture(0)

            if not camera.isOpened():

                toast(
                    "Camera not found"
                )

                return None

            width = int(
                camera.get(
                    cv2.CAP_PROP_FRAME_WIDTH
                )
            )

            height = int(
                camera.get(
                    cv2.CAP_PROP_FRAME_HEIGHT
                )
            )

            if width <= 0:
                width = 640

            if height <= 0:
                height = 480

            fps = camera.get(
                cv2.CAP_PROP_FPS
            )

            if fps <= 0 or fps > 60:

                fps = 20.0

            fourcc = cv2.VideoWriter_fourcc(
                *"mp4v"
            )

            writer = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (width, height)
            )

            if not writer.isOpened():

                toast(
                    "Unable to create video"
                )

                return None

            print(
                "Video recording started"
            )

            print(
                "Press SPACE to stop"
            )

            print(
                "Press ESC to cancel"
            )

            while True:

                success, frame = (
                    camera.read()
                )

                if not success:

                    break

                writer.write(
                    frame
                )

                cv2.imshow(
                    "Safivox - Record Video",
                    frame
                )

                key = (
                    cv2.waitKey(1)
                    &
                    0xFF
                )

                # SPACE
                if key == 32:

                    break

                # ESC
                if key == 27:

                    if os.path.isfile(
                        output_path
                    ):

                        try:

                            os.remove(
                                output_path
                            )

                        except Exception:

                            pass

                    self.status_text = (
                        "Video recording cancelled"
                    )

                    return None

            if writer:

                writer.release()

            if camera:

                camera.release()

            cv2.destroyAllWindows()

            if os.path.isfile(
                output_path
            ):

                print(
                    "Video saved:",
                    output_path
                )

                self.finish_video(
                    output_path
                )

                return output_path

            toast(
                "Video was not saved"
            )

            return None

        except Exception as e:

            print(
                "Video recording error:",
                e
            )

            self.status_text = (
                "Video recording failed"
            )

            return None

        finally:

            try:

                if writer:

                    writer.release()

            except Exception:

                pass

            try:

                if camera:

                    camera.release()

            except Exception:

                pass

            try:

                cv2.destroyAllWindows()

            except Exception:

                pass

    # ==========================================================
    # FINISH VIDEO
    # ==========================================================

    def finish_video(
        self,
        path
    ):

        if not os.path.isfile(path):

            return

        self.refresh_counts()

        self.status_text = (
            "Video saved successfully"
        )

        print(
            "VIDEO SAVED:",
            path
        )

        if platform == "android":

            self.export_to_android_media(
                path,
                "video"
            )

        toast(
            "Video saved successfully"
        )

    # ==========================================================
    # RECORD AUDIO
    # ==========================================================

    def record_audio(self):

        self.ensure_directories()

        output_path = os.path.join(
            self.audio_dir,
            self.create_filename(
                "audio",
                ".wav"
            )
        )

        print(
            "Audio output:",
            output_path
        )

        # Android recording can be implemented
        # with the Android recorder module later.
        if platform == "android":

            toast(
                "Android audio recorder module required"
            )

            self.status_text = (
                "Android audio recorder not connected"
            )

            return None

        # Windows
        self.status_text = (
            "Recording audio for 5 seconds..."
        )

        thread = threading.Thread(
            target=self.record_audio_worker,
            args=(output_path,),
            daemon=True
        )

        thread.start()

        return output_path

    # ==========================================================
    # AUDIO WORKER
    # ==========================================================

    def record_audio_worker(
        self,
        output_path
    ):

        try:

            import sounddevice as sd
            from scipy.io.wavfile import write

            sample_rate = 44100

            duration = 5

            print(
                "Audio recording started"
            )

            recording = sd.rec(
                int(
                    duration *
                    sample_rate
                ),
                samplerate=sample_rate,
                channels=1,
                dtype="int16"
            )

            sd.wait()

            write(
                output_path,
                sample_rate,
                recording
            )

            print(
                "Audio saved:",
                output_path
            )

            Clock.schedule_once(
                lambda dt:
                self.finish_audio(
                    output_path
                )
            )

        except Exception as e:

            print(
                "Audio recording error:",
                e
            )

            Clock.schedule_once(
                lambda dt:
                self.audio_failed(
                    str(e)
                )
            )

    # ==========================================================
    # FINISH AUDIO
    # ==========================================================

    def finish_audio(
        self,
        path
    ):

        if not os.path.isfile(path):

            self.audio_failed(
                "Audio file was not created"
            )

            return

        self.refresh_counts()

        self.status_text = (
            "Audio saved successfully"
        )

        print(
            "AUDIO SAVED:",
            path
        )

        if platform == "android":

            self.export_to_android_media(
                path,
                "audio"
            )

        toast(
            "Audio saved successfully"
        )

    # ==========================================================
    # AUDIO ERROR
    # ==========================================================

    def audio_failed(
        self,
        error
    ):

        print(
            "Audio failed:",
            error
        )

        self.status_text = (
            "Audio recording failed"
        )

        toast(
            "Audio recording failed"
        )

    # ==========================================================
    # ANDROID MEDIA EXPORT
    # ==========================================================

    def export_to_android_media(
        self,
        source_path,
        media_type
    ):
        """
        Export to Android shared media.

        image -> Pictures/Safivox
        video -> Movies/Safivox
        audio -> Music/Safivox
        """

        if platform != "android":

            return False

        if not source_path:
            return False

        if not os.path.isfile(
            source_path
        ):

            return False

        try:

            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            ContentValues = autoclass(
                "android.content.ContentValues"
            )

            MediaStore = autoclass(
                "android.provider.MediaStore"
            )

            activity = (
                PythonActivity.mActivity
            )

            resolver = (
                activity.getContentResolver()
            )

            filename = os.path.basename(
                source_path
            )

            values = ContentValues()

            # ==================================================
            # IMAGE
            # ==================================================

            if media_type == "image":

                collection = (
                    MediaStore.Images.Media
                    .getContentUri(
                        "external"
                    )
                )

                values.put(
                    MediaStore.Images.Media.DISPLAY_NAME,
                    filename
                )

                values.put(
                    MediaStore.Images.Media.MIME_TYPE,
                    "image/jpeg"
                )

                values.put(
                    MediaStore.Images.Media.RELATIVE_PATH,
                    "Pictures/Safivox"
                )

                values.put(
                    MediaStore.Images.Media.IS_PENDING,
                    1
                )

            # ==================================================
            # VIDEO
            # ==================================================

            elif media_type == "video":

                collection = (
                    MediaStore.Video.Media
                    .getContentUri(
                        "external"
                    )
                )

                values.put(
                    MediaStore.Video.Media.DISPLAY_NAME,
                    filename
                )

                values.put(
                    MediaStore.Video.Media.MIME_TYPE,
                    "video/mp4"
                )

                values.put(
                    MediaStore.Video.Media.RELATIVE_PATH,
                    "Movies/Safivox"
                )

                values.put(
                    MediaStore.Video.Media.IS_PENDING,
                    1
                )

            # ==================================================
            # AUDIO
            # ==================================================

            elif media_type == "audio":

                collection = (
                    MediaStore.Audio.Media
                    .getContentUri(
                        "external"
                    )
                )

                values.put(
                    MediaStore.Audio.Media.DISPLAY_NAME,
                    filename
                )

                values.put(
                    MediaStore.Audio.Media.MIME_TYPE,
                    "audio/wav"
                )

                values.put(
                    MediaStore.Audio.Media.RELATIVE_PATH,
                    "Music/Safivox"
                )

            else:

                print(
                    "Unknown media type:",
                    media_type
                )

                return False

            uri = resolver.insert(
                collection,
                values
            )

            if uri is None:

                print(
                    "MediaStore insert failed"
                )

                return False

            output_stream = (
                resolver.openOutputStream(
                    uri
                )
            )

            if output_stream is None:

                return False

            try:

                with open(
                    source_path,
                    "rb"
                ) as source:

                    while True:

                        chunk = source.read(
                            1024 * 1024
                        )

                        if not chunk:

                            break

                        output_stream.write(
                            chunk
                        )

            finally:

                output_stream.close()

            # Remove pending state for
            # photos/videos.
            if media_type in (
                "image",
                "video"
            ):

                clear_values = (
                    ContentValues()
                )

                clear_values.put(
                    MediaStore.Images.Media.IS_PENDING,
                    0
                )

                try:

                    resolver.update(
                        uri,
                        clear_values,
                        None,
                        None
                    )

                except Exception as e:

                    print(
                        "Pending-state update:",
                        e
                    )

            print(
                "Exported to Android media:",
                uri.toString()
            )

            return True

        except Exception as e:

            print(
                "Android MediaStore error:",
                e
            )

            return False

    # ==========================================================
    # GET EVIDENCE PATHS
    # ==========================================================

    def get_photo_files(self):

        return self.get_files(
            self.photo_dir,
            [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ]
        )

    def get_video_files(self):

        return self.get_files(
            self.video_dir,
            [
                ".mp4",
                ".avi",
                ".mov",
                ".mkv"
            ]
        )

    def get_audio_files(self):

        return self.get_files(
            self.audio_dir,
            [
                ".wav",
                ".mp3",
                ".m4a",
                ".aac"
            ]
        )

    # ==========================================================
    # DELETE LOCAL EVIDENCE
    # ==========================================================

    def delete_local_evidence(
        self,
        file_path
    ):

        try:

            if os.path.isfile(
                file_path
            ):

                os.remove(
                    file_path
                )

            self.refresh_counts()

            toast(
                "Evidence deleted from Safivox"
            )

            return True

        except Exception as e:

            print(
                "Evidence delete error:",
                e
            )

            return False

    # ==========================================================
    # BACK
    # ==========================================================

    def go_back(self):

        if self.manager:

            self.manager.current = (
                "home"
            )