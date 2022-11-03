"""converter."""

import os
from pathlib import Path
from shutil import copy, make_archive
from tempfile import TemporaryDirectory
from typing import Callable
import threading
import uuid

from patoolib import extract_archive
from patoolib.util import PatoolError
from PIL import Image
from preferences import Preferences

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # noqa: E402


def check_cancel_process(func):
    """Check if a cancellation request has been made.

    Args:
        func (Callable): a function
    """
    def wrapper(*args, **kwargs):
        if args[0].event.is_set():
            def stop_process(*args, **kwargs):
                raise Exception("Conversion stopped by user")
            return stop_process()
        else:
            return func(*args, **kwargs)
    return wrapper


class Converter():
    """A utility class to extract and convert."""

    def __init__(self, files_to_convert: dict, event: threading.Event, reinit_ui_method: Callable):
        """Initialize the converter class.

        Args:
            files_to_convert (dict): a file path and a list [spinner, image_ok, image_error]
            event (threading.Event): an event to signal a request to end processing
            reinit_ui_method (Callable): a method executed at the end of processing
        """
        self.files_to_convert = files_to_convert
        self.event = event
        self.reinit_ui_method = reinit_ui_method

        self.preferences = Preferences()

        self.archive_formats = {
            "cbz": "zip",
            "zip": "zip",
        }

    def run(self):
        """Run the convert."""
        for file in self.files_to_convert:
            if self.event.is_set():
                break

            file["image_ok"].hide()
            file["image_error"].hide()
            file["spinner"].start()
            try:
                with TemporaryDirectory() as extract_dir_path:
                    archive_path = Path(file["file_path"])
                    if archive_path.is_file():
                        file["spinner"].set_tooltip_text("Extracting the archive")
                        self.extract_archive(file["file_path"], extract_dir_path)
                        with TemporaryDirectory() as convert_dir_path:
                            file["spinner"].set_tooltip_text("Image conversion")
                            self.convert_image(extract_dir_path, convert_dir_path)
                            file["spinner"].set_tooltip_text("Creating an archive file")
                            self.create_archive(file["file_path"], convert_dir_path)
                            file["image_ok"].show()
                    else:
                        file["image_error"].show()
                        file["image_error"].set_tooltip_text("Archive file does not exist")

            except PatoolError as err:
                file["image_error"].show()
                file["image_error"].set_tooltip_text(err)
            except Exception as err:
                file["image_error"].show()
                file["image_error"].set_tooltip_text(str(err))

            file["spinner"].stop()

        GLib.idle_add(self.reinit_ui_method)

    @ check_cancel_process
    def extract_archive(self, file_path: str, extract_dir_path: str):
        """Extract the archive file.

        Args:
            file_path (str): file path
            extract_dir_path (str): a directory path where the images will be extracted
        """
        extract_archive(file_path, outdir=extract_dir_path, verbosity=-1, interactive=False)

    @ check_cancel_process
    def convert_image(self, extract_dir_path: str, convert_dir_path: str):
        """Convert an image file.

        Args:
            extract_dir_path (str): a directory path where the images are located
            convert_dir_path (str): a directory path where the images will be converted
        """
        extract_path = Path(extract_dir_path)
        convert_path = Path(extract_dir_path)
        if extract_path.is_dir() and convert_path.is_dir():
            for root, dirs, files in os.walk(extract_path):
                root_dst = root.replace(extract_dir_path, convert_dir_path)
                for dir_name in dirs:
                    os.mkdir(Path(root_dst, dir_name))
                for file_name in files:
                    try:
                        image = Image.open(Path(root, file_name))
                        image.convert("RGB")

                        if self.preferences.get_value("image_size") == self.preferences.OUTPUT_CUSTOM_IMAGE_SIZE:
                            image.thumbnail((int(self.preferences.get_value("image_width")), int(self.preferences.get_value("image_height"))))

                        image.save(os.path.splitext(Path(root_dst, file_name))[0]+"." +
                                   self.preferences.get_value("image_format"), optimize=True, quality=100)
                    except Exception:
                        # It's not a picture
                        copy(Path(root, file_name), Path(root_dst, file_name))

    @ check_cancel_process
    def create_archive(self, file_path: str, dir_path: str):
        """Create an archive file.

        Args:
            file_path (str): the file path being converted
            dir_path (str): a directory path where the converted images are located
        """
        path = Path(file_path)
        file_name = path.stem

        output_folder = self.preferences.get_value("output_folder")
        if output_folder == self.preferences.OUTPUT_SELECTED_FOLDER:
            output_dir = self.preferences.get_value("selected_folder")
        else:
            output_dir = str(path.parent)

        # rename format cbz, cbr
        rename_output_archive_format = self.preferences.get_value("archive_format")
        output_archive_format = self.archive_formats[rename_output_archive_format]

        if output_dir is not None:
            # generate a random string to not erase the original file if the output folder is the same folder as the original
            file_name_tmp = str(uuid.uuid4())
            output_path = str(Path(output_dir, file_name_tmp))
            make_archive(output_path, output_archive_format, dir_path)
            # rename file name and file format
            os.rename(output_path + "." + output_archive_format, str(Path(output_dir, file_name)) + "." + rename_output_archive_format)
