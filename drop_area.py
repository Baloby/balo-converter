"""Drop area."""

from pathlib import Path
from urllib.parse import unquote, urlparse

import gi
from patoolib import test_archive
from patoolib.util import PatoolError

from error_dialog import ErrorDialog

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402


class DropArea(Gtk.ListBox):
    """Drop area.

    Args:
        Gtk (Gtk.ListBox): a list box
    """

    def __init__(self):
        """Initialize the drop area."""
        Gtk.ListBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.NONE)

        enforce_target = Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), 0)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [enforce_target], Gdk.DragAction.COPY)
        self.connect("drag-data-received", self.on_drag_data_received)

    def on_drag_data_received(self, widget, drag_context: Gdk.DragContext, x: int, y: int,
                              data: Gtk.SelectionData, info: int, time: int):
        """When the drag area received an elemnt.

        Args:
            widget (DropArea): a drop area
            drag_context (Gdk.DragContex): a context
            x (int): x
            y (int): y
            data (Gtk.SelectionData): a data
            info (int): an info
            time (int): a time
        """
        files_path = []
        for uri in data.get_uris():
            files_path.append(unquote(urlparse(uri).path))

        self.add_archives(files_path)

    def is_in_list(self, file_path: str):
        """Check if the file is already in the drop area.

        Args:
            file (str): a file path

        Returns:
            bool: return true if the file is already in the drop area
        """
        in_list = False
        for row in self.get_children():
            children = row.get_child().get_children()
            for widget in children:
                if widget.get_name() == "GtkLabel" and widget.get_text() == file_path:
                    in_list = True
                    break
            if in_list:
                break

        return in_list

    def add_archives(self, files_path: str):
        """Add archive to the list.

        Args:
            file_path (str): a file path
        """
        files_errors = []
        for file_path in files_path:
            archive_path = Path(file_path)
            if archive_path.is_file() and not self.is_in_list(file_path):
                try:
                    test_archive(file_path, verbosity=-1, interactive=False)
                except PatoolError:
                    files_errors.append("Invalid archive file : " + file_path)
                else:
                    row = Gtk.ListBoxRow()
                    hbox = Gtk.HBox(spacing=50)
                    row.add(hbox)

                    label = Gtk.Label(label=file_path, xalign=0)
                    button_remove = Gtk.Button.new_from_icon_name("list-remove-symbolic", Gtk.IconSize.BUTTON)
                    button_remove.connect("clicked", self.on_button_remove)

                    hbox_process = Gtk.HBox(spacing=5)
                    spinner = Gtk.Spinner()
                    image_ok = Gtk.Image.new_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
                    image_ok.set_no_show_all(True)
                    image_error = Gtk.Image.new_from_icon_name("emblem-important-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
                    image_error.set_no_show_all(True)
                    hbox_process.pack_start(spinner, False, True, 5)
                    hbox_process.pack_start(image_ok, False, True, 5)
                    hbox_process.pack_start(image_error, False, True, 5)

                    hbox.pack_start(button_remove, False, True, 5)
                    hbox.pack_start(label, True, True, 5)
                    hbox.pack_start(hbox_process, False, True, 5)
                    self.add(row)

        self.show_all()
        if files_errors:
            ErrorDialog("Error while adding archives", files_errors)

    def on_button_remove(self, button: Gtk.Button):
        """Remove the file path from the list.

        Args:
            button (Gtk.Button): a button clicked
        """
        row = button.get_ancestor(Gtk.ListBoxRow)
        self.remove(row)

    def remove_all(self):
        """Remove all archives from the listBox."""
        for row in self.get_children():
            self.remove(row)

    def get_files_to_convert(self):
        """Get the file paths and hbox to convert."""
        files_to_convert = []
        for row in self.get_children():
            children = row.get_child().get_children()
            for widget in children:
                if isinstance(widget, Gtk.Label):
                    file_path = widget.get_text()
                elif isinstance(widget, Gtk.HBox):
                    hbox = widget.get_children()

            if file_path and hbox:
                files_to_convert.append({"file_path": file_path, "spinner": hbox[0], "image_ok": hbox[1], "image_error": hbox[2]})

        return files_to_convert
