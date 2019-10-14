
from .note_list import NoteList
import os, sys
from stat import *
from .settings_manager import *
class BrowserNoteList(NoteList):

    def __init__(self, container, scrollview):
        super().__init__(container, scrollview)

    def get_objects(self):

        files = os.listdir(settingsManager.getNotePath()+"/")
        ret = {}
        ret['files'] = []
        for name in files:
            file = "/"+name
            ret['files'].append(file)
        return ret['files']


