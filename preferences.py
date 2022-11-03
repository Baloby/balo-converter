"""Key file."""

import os
from pathlib import Path
from typing import Union
from error_dialog import ErrorDialog

from gi.repository import GLib


class Preferences():
    """Key file.

    Args:
        Gtk (GLib.KeyFile): a key file
    """

    OUTPUT_SAME_FOLDER = "SAME"
    OUTPUT_SELECTED_FOLDER = "SELECTED"

    OUTPUT_ORIGINAL_IMAGE_SIZE = "ORIGINAL"
    OUTPUT_CUSTOM_IMAGE_SIZE = "CUSTOM"

    DEFAULT_IMAGE_WIDTH = "400"
    DEFAULT_IMAGE_HEIGHT = "800"
    DEFAULT_IMAGE_FORMAT = "png"
    DEFAULT_GROUP = "preferences"

    def __init__(self):
        """Initialize preferences."""
        self.config_dir = os.path.join(GLib.get_user_config_dir(), "balo-converter")
        self.config_file = os.path.join(self.config_dir, "balo-converter.conf")
        self.key_file = GLib.KeyFile.new()
        self.load()

    def load(self):
        """Load key file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            self.key_file.load_from_file(self.config_file, GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        except OSError as error:
            ErrorDialog("Configuration directory can not be created", error.args)
        except Exception:
            self.key_file.set_value(self.DEFAULT_GROUP, "selected_folder", str(Path.home()))
            self.key_file.set_value(self.DEFAULT_GROUP, "output_folder", self.OUTPUT_SAME_FOLDER)
            self.key_file.set_value(self.DEFAULT_GROUP, "archive_format", "cbz")
            self.key_file.set_value(self.DEFAULT_GROUP, "image_format", "png")
            self.key_file.set_value(self.DEFAULT_GROUP, "image_size", self.OUTPUT_ORIGINAL_IMAGE_SIZE)
            self.key_file.set_value(self.DEFAULT_GROUP, "image_width", self.DEFAULT_IMAGE_WIDTH)
            self.key_file.set_value(self.DEFAULT_GROUP, "image_height", self.DEFAULT_IMAGE_HEIGHT)
            self.key_file.save_to_file(self.config_file)

    def set_value(self, key: str, value: Union[str, int]):
        """Set the value for a key in the key file.

        Args:
            key (str): a key
            value (Union[str, int]): a value
        """
        self.key_file.set_value(self.DEFAULT_GROUP, key, value)
        self.key_file.save_to_file(self.config_file)

    def get_value(self, key: str):
        """Set the value for a key in the key file.

        Args:
            key (str): a key
            value (Union[str, int]): a value
        """
        try:
            value = self.key_file.get_value(self.DEFAULT_GROUP, key)
        except Exception:
            value = None

        return value
