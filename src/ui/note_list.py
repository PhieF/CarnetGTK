from .note_manager import NoteManager
from .settings_manager import *
from .note_widget import *
import os, sys
from stat import *
class NoteList:
    def __init__(self, container, scrollview):
        self.container = container

        self.scrollview = scrollview
        self.objects = self.get_objects()
        self.row = 0
        self.putNext(20)


        self.container.get_vadjustment().connect("value-changed",self.onChanged)


    def putNext(self, number):
        stopAt = self.row + number
        while( self.row != len(self.objects) and self.row < stopAt):
            path = self.objects[self.row]
            try:
                s = os.stat(settingsManager.getNotePath()+"/"+path)
                if(S_ISDIR(s.st_mode)):
                    row = row + 1
                    continue
            except Exception:
                print("bla")
            noteManager = NoteManager(settingsManager.getNotePath()+"/"+path)
            note = noteManager.getCachedMetadata()
            note['path'] = path
            note_widget = NoteWidget(note)
            note_widget.show_all()
            note_widget.connect("button-release-event", self.on_note_clicked)
            self.container.add_child(note_widget)
            self.row = self.row+1
        self.container.show_all()

    def set_window(self, window):
        self.window = window

    def on_note_clicked(self, note_widget, bla):
        print("clicked ! "+note_widget.note['path'])
        self.window.switch_to_editor(note_widget.note['path'])
    def get_objects(self):
        return False

    def onChanged(self, adjustment):
        #what remains
        if(adjustment.get_upper() - adjustment.get_value() -  adjustment.get_page_size()<10):
            self.putNext(10)

