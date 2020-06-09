# adaptive_grid.py
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


class AdaptiveGrid(Gtk.ScrolledWindow):
    __gtype_name__ = 'AdaptiveGrid'
    children = list()
    def __init__(self):
        super().__init__()
        self.gtk_box = Gtk.Box()
        self.gtk_box.set_homogeneous(True)
        self.add_with_viewport(self.gtk_box)
        self.current  = 0
        self.children = list()
        self.columns = list()

        self.column_rows = None

    def reset(self):
        self.internal_reset()
        self.children = list()
        self.current = -1
        self.onResized()

    def internal_reset(self):
        for column in self.columns:
            for child in column.get_children():
                print("removing child")
                column.remove(child)
            self.gtk_box.remove(column)
    def set_columns_count(self, count):
        self.internal_reset()
        self.column_rows = list()
        self.columns = list()

        for i in range(0,count):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.column_rows.append(0)
            self.columns.append(box)

            self.gtk_box.pack_start(box, True, True, 5)
        for child in self.children:
            print("adding child back")
            self.internal_add_child(child)
    def onResized(self):
        newColumnCount = int(self.get_allocation().width/250)
        if(newColumnCount < 2):
            newColumnCount = 2

        if(self.current != newColumnCount):
            self.current = newColumnCount
            self.set_columns_count(self.current)
            self.show_all()
        #for column in  self.columns:
        #    column.set_size_request(self.get_allocation().width/ newColumnCount -20, 0)

            self.queue_draw()
    def add_child(self, child):
        self.children.append(child)
        if(self.column_rows != None): #wait for first resize
            self.internal_add_child(child)

    def internal_add_child(self, child):

        column = self.column_rows.index(min(self.column_rows))
        self.columns[column].pack_start(child, False, False, 0)
        height = child.size_request().height
        self.column_rows[column] = self.column_rows[column]+height



    
