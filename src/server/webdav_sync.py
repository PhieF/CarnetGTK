import webdav3.client as wc
from .settings_manager import *
from .sync_db import *
import lxml.etree as etree
from io import BytesIO
from re import sub
from webdav3 import *
from webdav3.exceptions import *
from webdav3.urn import Urn
from stat import *
import os
import tempfile
import filecmp
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

class MyUrn(Urn):
    def __init__(self, hree, etag, parent_path):
        super(MyUrn, self).__init__(hree)
        self.etag = etag
        if(not parent_path.endswith("/")):
            parent_path = parent_path+"/"
        self.short_path = parent_path + self.filename()

    def get_etag(self):
        return self.etag

class Sync():




    def connect(self):
        options = {
         'webdav_hostname': settingsManager.get_webdav_server(),
         'webdav_login':    settingsManager.get_webdav_username(),
         'webdav_password': settingsManager.get_webdav_password()
        }
        self.client = wc.Client(options)

    def list(self, remote_path="/"):
        def parse(directory_urn, response):

            try:
                response_str = response.content

                tree = etree.fromstring(response_str)
                hrees = [unquote(hree.text) for hree in tree.findall(".//{DAV:}href")]
                etags = [unquote(etag.text) for etag in tree.findall(".//{DAV:}getetag")]
                i=0
                ret = []
                for hree in hrees:
                    if(i == 0):
                        i = i+1
                        continue
                    urn = MyUrn(hree, etags[i], remote_path)
                    ret.append(urn)

                    i = i+1
                return ret
            except etree.XMLSyntaxError:

                return list()

        try:
            directory_urn = Urn(remote_path, directory=True)

            if directory_urn.path() != wc.Client.root:
                if not self.client.check(directory_urn.path()):
                    raise RemoteResourceNotFound(directory_urn.path())
            response = BytesIO()
            response = self.client.execute_request(action='list', path=directory_urn.quote())
            urns = parse(directory_urn, response)
            return urns

        except Exception:
            raise NotConnection(self.client.webdav.hostname)

    def visit_remote (self, path):
        print("visitRemote "+path)
        items = self.list(path)
        for item in items:
            print("item  "+self.correct_remote_path(item.short_path))
            new_db_item = DBItem.from_nc(self.correct_remote_path(item.short_path), item)
            db_item = self.sync_db.get(self.account, self.correct_remote_path(item.short_path))
            if(item.is_dir()):
                print("item db "+str(db_item))
                if(db_item == None or db_item['remote_etag'] != item.etag):
                    self.visit_remote(item.short_path)
                else:
                    print("already in DB")
                    ls = self.sync_db.get_list(self.account)
                    for in_folder in ls :
                        if(in_folder.startswith(db_item['path'])):
                            print("adding "+in_folder)
                            self.remote_files[in_folder] = ls[in_folder]
            if(db_item != None):
                db_item['remote_etag'] = new_db_item['remote_etag']
                self.sync_db.set(self.account, new_db_item['path'], db_item)
            else:
                self.sync_db.set(self.account, new_db_item['path'], new_db_item)
            self.remote_files[new_db_item['path']] = new_db_item

        self.sync_db.write()

    def handle_remote_items(self, remote_db_Item):
        if (remote_db_item == None):
            return
        print("handle_remote_items")

        in_db_item = self.sync_db.get(self.account, remote_db_item['path'])
        if (in_db_item == None):
            #download
            self.download_and_save(remote_db_item, cb)
        else:
            if (in_db_item.synced_etag == remote_db_item.synced_etag):
                #delete remote
                self.delete_remote_and_save(remote_db_item, cb)
            else:
                self.download_and_save(remote_db_item, cb)


    def visit_local(self, path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
               self.local_files.append(DBItem.from_fs(self.correct_local_path(os.path.join(root, name)), os.stat(os.path.join(root, name))))
            for name in dirs:
               self.local_files.append(DBItem.from_fs(self.correct_local_path(os.path.join(root, name)), os.stat(os.path.join(root, name))))



    def handle_local_items(self, local_db_item):
        if (local_db_item == None):
            return False
        in_db_item = self.sync_db.get(self.account, local_db_item['path']);
        print(local_db_item['path'])
        try:
            remote_db_item = self.remote_files[local_db_item['path']]
        except KeyError:
            remote_db_item = None
        if (remote_db_item != None):
            del self.remote_files[local_db_item['path']];


        if (in_db_item == None): #has never been synced
            if (remote_db_item == None): #is not on server
                #upload  and save
                print("not on server")
                self.upload_and_save(local_db_item)
            else: #is on server
                #conflict
                if (not local_db_item['ftype']):
                    print("conflict on " + local_db_item['path'])
                    self.fix_conflict(local_db_item, remote_db_item, cb)
                else:
                    self.save(local_db_item, remote_db_item)
                    return

        else: #has already been synced
            if (remote_db_item == None): #is not on server
                if (local_db_item['locallastmod'] == in_db_item['locallastmod']): # was already sent
                    #delete local...
                    self.delete_local_and_save(local_db_item)
                else:
                    #upload
                    print("not up to date on server")
                    self.upload_and_save(local_db_item)
            else: #is on server

                if (remote_db_item['remote_etag'] == in_db_item['synced_etag']):
                    if (local_db_item['locallastmod'] == in_db_item['locallastmod']):
                        print("nothing to do !")
                        return
                    else:
                        #upload
                        if (not in_db_item['ftype']):
                            sync.upload_and_save(local_db_item)
                        else:
                            self.save(local_db_item, remote_db_item)
                            return
                elif (local_db_item['locallastmod'] == in_db_item['locallastmod']):
                    #download
                    if (not local_db_item['ftype']):
                        self.download_and_save(remote_db_item)
                    else:
                        self.save(local_db_item, remote_db_item)
                        return
                else:
                    #conflict

                    if (not local_db_item['ftype']):
                        print("conflict on " + local_db_item['path'])
                        self.fix_conflict(local_db_item, remote_db_item)
                    else:
                        self.save(local_db_item, remote_db_item)
                        return

    def fix_conflict(self, local_db_item, remote_db_item):
        fpath = tempfile.gettempdir()+"/tmpconflictfix.sqd"
        self.download_file(self.remote_path + "/" + remote_db_item['path'], fpath)
        if(filecmp.cmp(fpath, self.local_path+"/"+local_db_item['path'], shallow=False)):
            #fixed
            os.remove(fpath)
            self.save(local_db_item, remote_db_item)
        else:
            print("real conflict... fixing")
            split_name = os.path.splitext(local_db_item['path'])
            new_name = split_name[0]+" conflit "+date
            if(len(split_name)>1):
                new_name += split_name[1]
            os.rename(local_db_item.path, os.path.join(os.path.dirname(local_db_item.path),new_name))
            os.rename(fpath,local_db_item.path)
            sync.save(local_db_item, remote_db_item)
    #broken in webdav client
    def download_file(self, remote_path, local_path):
        """Downloads file from WebDAV server and save it locally.
        More information you can find by link http://webdav.org/specs/rfc4918.html#rfc.section.9.4
        :param remote_path: the path to remote file for downloading.
        :param local_path: the path to save file locally.
        :param progress: progress function. Not supported now.
        """
        urn = Urn(remote_path)

        with open(local_path, 'wb') as local_file:
            response = self.client.execute_request('download', urn.quote())
            for block in response.iter_content(1024):
                local_file.write(block)
    def download_and_save(self, remote_db_item):
        print("downloading " + remote_db_item['path'])
        fpath = self.local_path + "/" + remote_db_item['path']
        if (remote_db_item["ftype"]):
            try:
                os.makedirs(fpath)
                if (success):
                    stat = sync.fs.statSync(fpath)
                    sync.save(DBItem.fromFS(sync.settingsHelper.getNotePath(), fpath, stat), remote_db_item)
                    sync.hasDownloadedSmt = true;
            except Error:
                print("error")
                self.exit()


        else:
            try:
                self.download_file(self.remote_path + "/" + remote_db_item['path'], fpath)
                stat = os.stat(fpath)
                self.save(DBItem.from_fs(self.correct_local_path(fpath), stat), remote_db_item)
                self.has_downloaded_smt = True;
            except Exception:
                print("Error downloading "+remote_db_Item.path);
                self.exit();


    def upload_and_save(self, local_db_item):
        print("uploading: "+local_db_item['path'])
        if(local_db_item['ftype']):
            self.client.mkdir(self.remote_path + "/"+ local_db_item['path'])
        else:

            self.client.upload_sync( self.remote_path + "/"+ local_db_item['path'],self.local_path + "/" + local_db_item['path'])
        self.save(local_db_item, self.get_info(self.remote_path + "/"+ local_db_item['path']))

    #client.info() not working...
    def get_info(self, path):
        items = self.list(os.path.dirname(path))
        for item in items:
            print(path + " "+item.short_path)
            if(item.short_path == path):
                return DBItem.from_nc(self.correct_remote_path(item.short_path), item)

    def save(self, local, remote):
        local['remote_etag'] = remote['remote_etag']
        local['synced_etag'] = remote['remote_etag']
        self.sync_db.set(self.account, local['path'], local)
        self.sync_db.write()

    def start_sync(self):
        self.connect()

        self.remote_files = {}
        self.local_files = []

        self.sync_db = SyncDB()
        self.account = 0
        self.local_path = "/home/phieubuntu/Carnet"
        self.remote_path = "/Documents/QuickNote"

        self.visit_remote(self.remote_path)
        self.visit_local(self.local_path)
        for item in self.local_files:
            self.handle_local_items(item)

    def correct_local_path (self, path):
        local_path = self.local_path
        if (path.startswith(local_path)):
            path = path[len(local_path):]
        if (path.startswith("/")):
            path = path[1:]
        print("local path "+path)
        return path;

    def correct_remote_path (self, path):
        if (path.startswith(self.remote_path)):
            path = path[len(self.remote_path):]
        if (path.startswith("/" + self.remote_path)):
            path = path[len(self.remote_path)+ 1:]
        if (path.startswith("/")):
            path = path[1:]
        if (path.endswith("/")):
            path = path[:len(path)-1]
        return path


class DBItem():


    def from_nc(path, ncitem):
        dbitem = {}
        dbitem['path'] = path
        dbitem['locallastmod'] = None
        dbitem['synced_etag'] = None
        dbitem['remote_etag'] = ncitem.get_etag()
        dbitem['ftype'] =ncitem.is_dir()

        return dbitem

    def from_fs(path, stat):
        dbitem = {}
        dbitem['path'] =path
        dbitem['locallastmod'] = stat.st_mtime
        dbitem['synced_etag'] = None
        dbitem['remote_etag'] = None

        if S_ISDIR(stat.st_mode):
            dbitem['ftype'] = True
        else:
            dbitem['ftype'] = False
        return dbitem
