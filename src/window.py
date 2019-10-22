# window.py
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
import gi
from gi.repository import Gtk, Gdk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2
from .gi_composites import GtkTemplate
from .settings_manager import *
from .adaptive_grid import *
from .overview import *
from .overview_toolbar import *
from .editor_toolbar import *
from .recent_db_manager import RecentDBManager
from .recent_note_list import RecentNoteList
@GtkTemplate(ui='/org/gnome/Carnetgtk/ui/res/window.ui')
class CarnetgtkWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'CarnetgtkWindow'


    overview = GtkTemplate.Child()
    header_bar = GtkTemplate.Child()
    editor_toolbar = GtkTemplate.Child()
    #overview_toolbar = GtkTemplate.Child()
    main_view = GtkTemplate.Child()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #WebKit2.WebView()
        self.init_template()

        css_provider = Gtk.CssProvider.get_default()
        css_provider.load_from_data(b""".note2
        {
        border-radius: 5px;

        }
        .note_none{
                background:white;
                border:solid 1px #e0e0e0;
        }
       .note_red{
            background: rgb(241, 166, 166);
        }
        .note_orange{
            background: rgb(241, 195, 165);
        }
        .note_yellow{
            background: rgb(255, 230, 157);
        }

        .note_green{
            background: rgb(174, 243, 190);
        }
        .note_teal{
            background: rgb(108, 247, 240);
        }
        .note_blue{
            background: rgb(122, 167, 201);
            box-shadow:none;
        }
        .note_violet{
            background: rgb(155, 135, 199);
            box-shadow:none;
        }
        .note_purple{
            background: rgb(178, 137, 192);
        }
        .note_pink{
            background: rgb(207, 157, 185);
        }

        /*.note-title{
           color:white;
        }

        .note-text{
           color:white;
        }*/
""")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.set_titlebar(self.overview.header_bar)

        #self.webview.load_uri("file:///home/phieelementary/Dev/GitBis/QuickDoc/CarnetNextcloud/templates/CarnetElectron/index.html")
        #self.webview.connect("notify::title", self.window_title_change) #only way to receive messages...
        #self.webview.load_uri("http://localhost:8087")
        self.connect('check-resize', self.resized)
        self.editor_toolbar.set_window(self)
        self.overview.set_window(self)
        #self.webview.get_inspector().detach()
        #self.note_container.insert_row(1)
        #self.note_container.insert_column(1)
        #self.editor_toolbar.hide()
    def resized(self, window):
        self.editor_toolbar.on_resize(self.get_allocation().width)
        self.overview.onResized()

    def convert_to_hex(self, rgba_color) :
        red = int(rgba_color.red*255)
        green = int(rgba_color.green*255)#self.webview.load_uri("file:///home/phieelementary/Dev/GitBis/QuickDoc/CarnetNextcloud/templates/CarnetElectron/index.html")
        #self.webview.connect("notify::title", self.window_title_change) #only way to receive messages...
        #self.webview.load_uri("http://localhost:8087")
        self.switch_to_browser()
        RecentNoteList(self.note_container, self.scroll)
        #self.webview.get_inspector().detach()
        blue = int(rgba_color.blue*255)
        return '{r:02x}{g:02x}{b:02x}'.format(r=red,g=green,b=blue)


    def toggle_toolbar(self, toolbar):
        self.webview.run_javascript("writer.toolbarManager.toggleToolbar(writerFrame.contentWindow.document.getElementById('"+toolbar+"'))")

    def window_title_change(self, v, param):
        print("on title changed")
        if not v.get_title():
            return
        if v.get_title().startswith("msgtopython:::"):
            message = v.get_title().split(":::",1)[1]
            # Now, send a message back to JavaScript
            if(message == "noteloaded"):
                print('loaded')
            elif(message == "exit"):
                self.switch_to_browser()

    def switch_to_editor(self, path):

        if(not hasattr(self, "webview")):
            self.webview = WebKit2.WebView()
            self.webview.load_uri("http://localhost:9098/reader/reader.html?path="+path)
            self.webview.connect("notify::title", self.window_title_change) #only way to receive messages...
            self.main_view.add(self.webview)
            self.main_view.show_all()
        else:
            self.webview.run_javascript("loadPath(\""+path+"\")")

        self.overview.hide()
        self.set_titlebar(self.header_bar)
        self.webview.show()

        self.webview.get_inspector().detach()
        #for child in self.header_bar.get_children():
        #    if(child.get_name() == "new-note"):
        #        child.hide()
        #    elif(child.get_name() == "new-folder"):
        #        child.hide()
        #for child in self.header_bar.get_custom_title().get_children():
        #    if(child.get_name() == "title-label"):
        #        child.hide()
        #    elif(child.get_name() == "editor-box"):
        #        child.show()
    def switch_to_browser(self):
        self.set_titlebar(self.overview.header_bar)
        self.overview.show()
        self.webview.hide()

