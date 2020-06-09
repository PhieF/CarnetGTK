import json
import os
import sqlite3
class SyncDB:

    def __init__(self):

        try:
            file = open('sync_db.json', 'r')
            text = file.read()
            print(text)
            file.close()
            self.sync_db = json.loads(text)
        except FileNotFoundError:
            self.sync_db = {}
        except json.decoder.JSONDecodeError:
            self.sync_db = {}

    def set(self,account, key, value):
        try:
            self.sync_db[str(account)][key] = value
        except KeyError:
            self.sync_db[str(account)] = {}
            self.sync_db[str(account)][key] = value

    def get_list(self, account):
        try:
            return self.sync_db[str(account)]
        except KeyError:
            return None

    def get(self,account, key):
        try:
            return self.sync_db[str(account)][key]
        except KeyError:
            return None

    def delete(self,account, key):
        del self.sync_db[str(account)][key]

    def write(self):
        file = open('sync_db.json', 'w')
        file.write(json.dumps(self.sync_db))
        file.close()
