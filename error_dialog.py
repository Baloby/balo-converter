"""Error dialog."""


from typing import Union

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


class ErrorDialog(Gtk.MessageDialog):
    """Show a error dialog.

    Args:
        Gtk (Gtk.MessageDialog): a message dialog
    """

    def __init__(self, message: str, secondary_text: Union[list, tuple]):
        """Init the error dialog.

        Args:
            message (str): primary text_
            secondary_text (Union[list, tuple]): secondary text
        """
        super().__init__(flags=Gtk.DialogFlags.MODAL,
                         type=Gtk.MessageType.ERROR,
                         buttons=Gtk.ButtonsType.CLOSE,
                         message_format=message)

        format_secondary_text = "\n".join(secondary_text)
        self.format_secondary_text(format_secondary_text)

        response = self.run()
        if response:
            self.destroy()
