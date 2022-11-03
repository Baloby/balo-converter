"""Main."""


import sys

import gi

from window import Window

gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf, Gio, Gtk  # noqa: E402


class Application(Gtk.Application):
    """Main application.

    Args:
        Gtk (Gtk.Application): an application
    """

    def __init__(self):
        """Initialize the applicaiton."""
        Gtk.Application.__init__(self)

    def do_startup(self):
        """When starting the application."""
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

    def do_activate(self):
        """When activating the application."""
        self.window = Window(self)
        self.window.resize(800, 600)
        self.window.show_all()

    def on_about(self, action: Gio.SimpleAction, param: None):
        """Open about dialog.

        Args:
            action (Gio.SimpleAction): an action
            param (None): None
        """
        if True:
            if True:
                print("ok")

        aboutdialog = Gtk.AboutDialog(transient_for=self.window, modal=True)

        aboutdialog.set_program_name("BaloConverter")
        aboutdialog.set_comments("A image converter")
        aboutdialog.set_version("1.0.0")
        aboutdialog.set_license_type(Gtk.License.GPL_3_0)
        aboutdialog.set_copyright("Copyright © 2022 Balob")
        aboutdialog.set_authors(["Balob"])
        aboutdialog.set_website("https://github.com/Baloby/balo-converter")
        aboutdialog.set_website_label("BaloConverter Website")

        pixbuf = GdkPixbuf.Pixbuf.new_from_file("baloconverter.ico")
        aboutdialog.set_logo(pixbuf)

        aboutdialog.run()
        aboutdialog.destroy()


app = Application()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
