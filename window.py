"""Window."""

import glob
import threading
from pathlib import Path
from patoolib import ArchiveFormats, ArchiveMimetypes
from converter import Converter
from drop_area import DropArea
from preferences import Preferences

import gi


gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk  # noqa: E402


class Window(Gtk.ApplicationWindow):
    """Window.

    Args:
        Gtk (Gtk.ApplicationWindow): an application window
    """

    def __init__(self, app):
        """Initialize the window.

        Args:
            app (Gtk.Application): an application
        """
        Gtk.Window.__init__(self, title="BaloConverter", application=app)
        self.set_icon_from_file("baloconverter.ico")

        self.icon_size = Gtk.IconSize.LARGE_TOOLBAR
        self.extentions = ArchiveFormats + ("cbz", "cbr")
        self.event_run = threading.Event()
        self.thread_run = None

        self.preferences = Preferences()

        self.create_action()
        self.create_header_bar()
        self.create_popover_preferences()

        self.drop_area = DropArea()
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.drop_area)
        self.status_bar = Gtk.Statusbar()

        vbox = Gtk.VBox()
        vbox.add(scrolled_window)
        vbox.pack_end(self.status_bar, False, False, 0)
        self.add(vbox)

    def create_action(self):
        """Create action."""
        # add archives
        action_add_archives = Gio.SimpleAction.new("add_archives")
        action_add_archives.connect("activate", self.on_add_archives)
        self.add_action(action_add_archives)

        # add folders
        action_add_folders = Gio.SimpleAction.new("add_folders")
        action_add_folders.connect("activate", self.on_add_folders)
        self.add_action(action_add_folders)

        # remove all
        action_remove_all = Gio.SimpleAction.new("remove_all")
        action_remove_all.connect("activate", self.on_remove_all)
        self.add_action(action_remove_all)

        # run
        action_run = Gio.SimpleAction.new("run")
        action_run.connect("activate", self.on_run)
        self.add_action(action_run)

        # preferences
        action_preferences = Gio.SimpleAction.new("preferences")
        action_preferences.connect("activate", self.on_preferences)
        self.add_action(action_preferences)

    def create_header_bar(self):
        """Create the toolbar.

        Returns:
            Gtk.Toolbar: a toolbar created
        """
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = "Balo-Converter"
        self.set_titlebar(header_bar)

        # add archives
        icon_add_archives = Gtk.Image.new_from_icon_name("list-add-symbolic", self.icon_size)
        self.button_add_archives = Gtk.ToolButton.new(icon_add_archives, "Add archives")
        self.button_add_archives.set_tooltip_text("Add archives")
        header_bar.pack_start(self.button_add_archives)
        self.button_add_archives.set_action_name("win.add_archives")

        # add folders
        icon_add_folders = Gtk.Image.new_from_icon_name("folder-new-symbolic", self.icon_size)
        self.button_add_folders = Gtk.ToolButton.new(icon_add_folders, "Add folders")
        self.button_add_folders.set_tooltip_text("Add folders")
        header_bar.pack_start(self.button_add_folders)
        self.button_add_folders.set_action_name("win.add_folders")

        # remove all
        icon_remove_all = Gtk.Image.new_from_icon_name("list-remove-all-symbolic", self.icon_size)
        self.button_remove_all = Gtk.ToolButton.new(icon_remove_all, "Remove all")
        self.button_remove_all.set_tooltip_text("Remove all")
        header_bar.pack_start(self.button_remove_all)
        self.button_remove_all.set_action_name("win.remove_all")

        # run
        icon_run = Gtk.Image.new_from_icon_name("system-run-symbolic", self.icon_size)
        self.button_run = Gtk.ToolButton.new(icon_run, "Start conversion")
        self.button_run.set_tooltip_text("Start conversion")
        header_bar.pack_start(self.button_run)
        self.button_run.set_action_name("win.run")

        # about
        icon_about = Gtk.Image.new_from_icon_name("help-about-symbolic", self.icon_size)
        button_about = Gtk.ToolButton.new(icon_about, "About")
        button_about.set_tooltip_text("About")
        header_bar.pack_end(button_about)
        button_about.set_action_name("app.about")

        # preferences
        icon_preferences = Gtk.Image.new_from_icon_name("preferences-system-symbolic", self.icon_size)
        self.button_preference = Gtk.ToolButton.new(icon_preferences, "Preferences")
        self.button_preference.set_tooltip_text("Preferences")
        header_bar.pack_end(self.button_preference)
        self.button_preference.set_action_name("win.preferences")

    def create_popover_preferences(self):
        """Create a popover for the preferences button."""
        self.popover = Gtk.Popover()
        vbox = Gtk.VBox()

        # Label output folder
        label_output_folder = Gtk.Label(xalign=0)
        label_output_folder.set_margin_left(5)
        label_output_folder.set_markup("<b> Output folder</b>")
        vbox.pack_start(label_output_folder, expand=True, fill=True, padding=10)

        # Button same folder
        radio_button_same_folder = Gtk.RadioButton.new_with_label_from_widget(None, "In the same folder as the source")
        radio_button_same_folder.set_margin_left(20)
        radio_button_same_folder.connect("toggled", self.on_button_output_folder_toggled, self.preferences.OUTPUT_SAME_FOLDER)
        vbox.add(radio_button_same_folder)

        # Button selected folder
        hbox_same_folder = Gtk.HBox()

        self.radio_button_selected_folder = Gtk.RadioButton.new_with_label_from_widget(
            radio_button_same_folder, "In the folder " + self.preferences.get_value("selected_folder"))
        self.radio_button_selected_folder.set_margin_left(20)
        self.radio_button_selected_folder.connect("toggled", self.on_button_output_folder_toggled, self.preferences.OUTPUT_SELECTED_FOLDER)
        hbox_same_folder.add(self.radio_button_selected_folder)

        if self.preferences.get_value("output_folder") == self.preferences.OUTPUT_SELECTED_FOLDER:
            self.radio_button_selected_folder.set_active(True)

        # Button select folder
        button_select_folder = Gtk.Button(label="Browse...")
        button_select_folder.set_image(Gtk.Image.new_from_icon_name("document-open-symbolic", Gtk.IconSize.BUTTON))
        button_select_folder.set_always_show_image(True)
        button_select_folder.connect("clicked", self.on_button_select_folder)
        hbox_same_folder.add(button_select_folder)

        vbox.add(hbox_same_folder)

        # Label output archive format
        label_output_formats = Gtk.Label(xalign=0)
        label_output_formats.set_margin_left(5)
        label_output_formats.set_markup("<b> Output archive format</b>")
        vbox.pack_start(label_output_formats, expand=True, fill=True, padding=10)

        # Label output archive formats
        hbox_output_archive = Gtk.HBox()

        label_archive_formats = Gtk.Label(label="Archive", xalign=0)
        hbox_output_archive.pack_start(label_archive_formats, expand=False, fill=False, padding=20)

        # Combo output archive format
        combo_archive_format = Gtk.ComboBoxText()
        combo_archive_format.set_entry_text_column(0)
        combo_archive_format.connect("changed", self.combo_archive_format_changed)
        for format in ["cbz", "zip"]:
            combo_archive_format.append(format, format)

        combo_archive_format.set_active_id(self.preferences.get_value("archive_format"))

        hbox_output_archive.pack_start(combo_archive_format, expand=False, fill=False, padding=0)

        vbox.add(hbox_output_archive)

        # Label output image format
        label_output_image_size = Gtk.Label(xalign=0)
        label_output_image_size.set_margin_left(5)
        label_output_image_size.set_markup("<b> Output image format</b>")
        vbox.pack_start(label_output_image_size, expand=True, fill=True, padding=10)

        # Label output image formats
        hbox_output_archive = Gtk.HBox()

        label_archive_formats = Gtk.Label(label="Image", xalign=0)
        hbox_output_archive.pack_start(label_archive_formats, expand=False, fill=False, padding=20)

        combo_image_format = Gtk.ComboBoxText()
        combo_image_format.set_entry_text_column(0)
        combo_image_format.connect("changed", self.combo_image_format_changed)
        for format in ["jpg", "png", "webp"]:
            combo_image_format.append(format, format)

        combo_image_format.set_active_id(self.preferences.get_value("image_format"))

        hbox_output_archive.pack_start(combo_image_format, expand=False, fill=False, padding=0)

        vbox.add(hbox_output_archive)

        # Label output image size
        label_output_image_size = Gtk.Label(xalign=0)
        label_output_image_size.set_margin_left(5)
        label_output_image_size.set_markup("<b> Output image size</b>")
        vbox.pack_start(label_output_image_size, expand=True, fill=True, padding=10)

        # Button original size
        hbox_same_folder = Gtk.HBox()

        self.radio_button_original_size = Gtk.RadioButton.new_with_label_from_widget(None, "Original size")
        self.radio_button_original_size.set_margin_left(20)
        self.radio_button_original_size.connect("toggled", self.on_button_image_size_toggled, self.preferences.OUTPUT_ORIGINAL_IMAGE_SIZE)
        vbox.add(self.radio_button_original_size)

        # Button custom image size
        hbox_custom_image_size = Gtk.HBox()

        self.radio_button_custom_image_size = Gtk.RadioButton.new_with_label_from_widget(
            self.radio_button_original_size, "Custom size")
        self.radio_button_custom_image_size.set_margin_left(20)
        self.radio_button_custom_image_size.connect("toggled", self.on_button_image_size_toggled, self.preferences.OUTPUT_CUSTOM_IMAGE_SIZE)
        hbox_custom_image_size.add(self.radio_button_custom_image_size)

        if self.preferences.get_value("image_size") == self.preferences.OUTPUT_CUSTOM_IMAGE_SIZE:
            self.radio_button_custom_image_size.set_active(True)

        # Label width
        label_width = Gtk.Label("Width", xalign=0)
        label_width.set_margin_left(5)
        label_width.set_margin_right(5)
        hbox_custom_image_size.add(label_width)

        # Entry width
        entry_width = Gtk.Entry()
        entry_width.set_text(self.preferences.get_value("image_width"))
        entry_width.set_width_chars(5)
        entry_width.connect("changed", self.on_entry_width_changed)
        hbox_custom_image_size.add(entry_width)

        # Label height
        label_height = Gtk.Label("Height", xalign=0)
        label_height.set_margin_left(5)
        label_height.set_margin_right(5)
        hbox_custom_image_size.add(label_height)

        # Entry height
        entry_height = Gtk.Entry()
        entry_height.set_text(self.preferences.get_value("image_height"))
        entry_height.set_width_chars(5)
        entry_width.connect("changed", self.on_entry_height_changed)
        hbox_custom_image_size.add(entry_height)

        vbox.add(hbox_custom_image_size)

        vbox.show_all()
        self.popover.add(vbox)
        self.popover.set_position(Gtk.PositionType.BOTTOM)
        self.popover.set_relative_to(self.button_preference)

    def on_add_archives(self, action: Gio.SimpleAction, parameter: None):
        """Add archives to list.

        Args:
            action(Gio.SimpleAction): an action
            param(None): None
        """
        dialog = Gtk.FileChooserDialog("Add archives", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))

        dialog.set_select_multiple(True)

        # filters
        filter_archive = Gtk.FileFilter()
        filter_archive.set_name("Archives")
        for mime_type, ext in ArchiveMimetypes.items():
            filter_archive.add_pattern("*.{0}".format(str(ext)))
            filter_archive.add_mime_type(mime_type)

        dialog.set_filter(filter_archive)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.drop_area.add_archives(dialog.get_filenames())

        dialog.destroy()

    def on_add_folders(self, action: Gio.SimpleAction, param: None):
        """Add folders to list.

        Args:
            action(Gio.SimpleAction): an action
            param(None): None
        """
        dialog = Gtk.FileChooserDialog("Add folders", self, Gtk.FileChooserAction.SELECT_FOLDER, (
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))

        dialog.set_select_multiple(True)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            files_path = []
            folders_path = dialog.get_filenames()
            for folder_path in folders_path:
                path = Path(folder_path)
                if path.is_dir():
                    for ext in self.extentions:
                        path_glob = str(path.joinpath(glob.escape(str(path)), "**/*." +
                                                      "".join("[%s%s]" % (e.lower(), e.upper()) for e in ext)))
                        files_path += glob.glob(path_glob, recursive=True)

            if files_path:
                self.drop_area.add_archives(files_path)

        dialog.destroy()

    def on_remove_all(self, action: Gio.SimpleAction, param: None):
        """Remove all archives from the drag area.

        Args:
            action(Gio.SimpleAction): an action
            param(None): None
        """
        self.drop_area.remove_all()

    def on_run(self, action: Gio.SimpleAction, param: None):
        """Run files conversion.

        Args:
            action(Gio.SimpleAction): an action
            param(None): None
        """
        if (self.thread_run is not None and self.thread_run.is_alive() and not self.event_run.is_set()):
            self.button_run.set_sensitive(False)
            self.button_run.set_label("Conversion stop request...")
            self.status_bar.push(0, "Conversion stop request...")
            self.event_run.set()
        else:
            files_to_convert = self.drop_area.get_files_to_convert()
            if files_to_convert:
                self.treatment_in_progress()
                converter = Converter(files_to_convert, self.event_run, self.processing_completed)
                self.thread_run = threading.Thread(target=converter.run)
                self.thread_run.daemon = True
                self.thread_run.start()

    def processing_completed(self, manual: bool = False):
        """Conversion processing completed."""
        # self.event_run.clear()
        # self.thread_run = None

        self.button_run.set_tooltip_text("Start conversion")
        self.button_run.set_sensitive(True)
        self.button_add_archives.set_sensitive(True)
        self.button_add_folders.set_sensitive(True)
        self.button_remove_all.set_sensitive(True)
        self.button_preference.set_sensitive(True)
        self.drop_area.set_sensitive(True)
        self.button_run.set_icon_widget(Gtk.Image.new_from_icon_name("system-run-symbolic", self.icon_size))
        self.status_bar.push(0, "Conversion complete")
        self.show_all()

    def treatment_in_progress(self):
        """Update the UI for the current conversion process."""
        self.status_bar.push(0, "Converting...")
        self.button_run.set_tooltip_text("Converting...")
        self.button_add_archives.set_sensitive(False)
        self.button_add_folders.set_sensitive(False)
        self.button_remove_all.set_sensitive(False)
        self.button_preference.set_sensitive(False)
        self.drop_area.set_sensitive(False)
        self.button_run.set_icon_widget(Gtk.Image.new_from_icon_name(
            "process-stop-symbolic", self.icon_size))
        self.show_all()

    def on_preferences(self, action: Gio.SimpleAction, param: None):
        """Open preferences.

        Args:
            action(Gio.SimpleAction): an action
            param(None): None
        """
        self.popover.popup()

    def on_button_output_folder_toggled(self, button: Gtk.RadioButton, value: str):
        """Set the output folder.

        Args:
            button (Gtk.RadioButton): a radio button
            value (str): SAME for default folder or SELECTED for selected folder
        """
        self.preferences.set_value("output_folder", value)

    def on_button_select_folder(self, button: Gtk.Button):
        """On the click of the "select folder" button, open the file chooser dialog.

        Args:
            button (Gtk.button): button clicked
        """
        dialog = Gtk.FileChooserDialog(title="Choose a folder", parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder_path = dialog.get_filename()
            self.preferences.set_value("selected_folder", folder_path)
            self.radio_button_selected_folder.set_label("In the folder " + self.preferences.get_value("selected_folder"))

        dialog.destroy()

    def combo_archive_format_changed(self, combo: Gtk.ComboBox):
        """Select output archive format.

        Args:
            combo (Gtk.ComboBox): a combo box
        """
        text = combo.get_active_text()
        self.preferences.set_value("archive_format", text)

    def combo_image_format_changed(self, combo: Gtk.ComboBox):
        """Select output image format.

        Args:
            combo (Gtk.ComboBox): a combo box
        """
        text = combo.get_active_text()
        self.preferences.set_value("image_format", text)

    def on_button_image_size_toggled(self, button: Gtk.RadioButton, value: str):
        """Set the image size.

        Args:
            button (Gtk.RadioButton): a radio button
            value (str): ORIGINAL for original size or CUSTOM for custom size
        """
        self.preferences.set_value("image_size", value)

    def on_entry_width_changed(self, entry):
        """Set the image width.

        Args:
            entry (Gtk.Entry): a entry
        """
        try:
            value = int(entry.get_text().strip())
            entry.set_text(str(value))
            self.preferences.set_value("image_width", str(value))

        except ValueError:
            entry.set_text(self.preferences.DEFAULT_IMAGE_WIDTH)

    def on_entry_height_changed(self, entry):
        """Set the image height.

        Args:
            entry (Gtk.Entry): a entry
        """
        try:
            value = int(entry.get_text().strip())
            entry.set_text(str(value))
            self.preferences.set_value("image_height", str(value))

        except ValueError:
            entry.set_text(self.preferences.DEFAULT_IMAGE_HEIGHT)
