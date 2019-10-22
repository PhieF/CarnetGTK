# main.py
#
# Copyright 2019 Phie
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import gi
import os
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '0.0')
from gi.repository import Gtk, Gio
import webdav3.client as wc
from .window import CarnetgtkWindow
from .server import Server
from .settings_manager import *
from .webdav_sync import Sync
os.environ["WEBKIT_INSPECTOR_SERVER"] = "127.0.0.1:1234"
class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='org.gnome.Carnetgtk',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        server = Server()
        server.start()
        #sync = Sync()
        #sync.start_sync()
        print("bla")
        #sync.start_sync()
        win = self.props.active_window
        if not win:
            win = CarnetgtkWindow(application=self)
        win.present()

def main(version):
    app = Application()
    return app.run(sys.argv)

win = None
