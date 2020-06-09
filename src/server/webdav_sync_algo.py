import webdav.client as wc
from stat import *
import tempfile
from .settings_manager import *
class Sync():
    def __init__(self, on_sync_start, on_sync_end):
        self.on_sync_start = on_sync_start
        self.on_sync_end = on_sync_end
        self.sync_next = []

    def connect(self):
        options = {
         'webdav_hostname': settingsManager.get_webdav_server(),
         'webdav_login':    settingsManager.get_webdav_username(),
         'webdav_password': settingsManager.get_webdav_password()
        }
        self.client = wc.Client(options)



    def start_sync(self, on_dir_ok):
        self.is_full_sync = on_dir_ok == -1
        if(on_dir_ok == None):
            on_dir_ok = self.on_dir_ok

        self.has_download_smt = False
        if(settingsManager.get_webdav_server() == None or settingsManager.get_webdav_username() == None or settingsManager.get_webdav_password() == None):
            self.exit()
            return False
        if(self.is_syncing):
            return False
        self.is_syncing = True
        self.on_sync_start()
        self.connect()
        self.nextcloud_root = settingsManager.get_webdav_path()

        file = open('sync_db.json', 'r')
        text = file.read()
        file.close()
        self.db = json.loads(text)
        self.remoteFiles = {}
        self.remoteFilesStack = []

        self.remoteFoldersToVisit = [];
        self.localFoldersToVisit = [];
        self.localFiles = [];
        self.localDirToRm = []
        self.remoteDirToRm = []
        self.toUpload = [];
        self.filesToStat = []
        self.toDownload = [];
        self.toFix = [];
        self.toDeleteLocal = [];
        self.toDeleteRemote = [];
        self.client.createDirectory(self.nextcloud_root).then(function () {
            on_dir_ok();
        }).catch(function (err) {
            print(err);
            on_dir_ok();
        });
        return True;

    def correctPath (nextcloudRoot, path):
        if (path.startswith(nextcloudRoot)):
            path = path.substr(nextcloudRoot.length)
        if (path.startswith("/" + nextcloudRoot)):
            path = path.substr(nextcloudRoot.length + 1)
        if (path.startswith("/")):
            path = path.substr(1)
        return path


    def correct_local_path (localRoot, path):
        if (path.startswith(localRoot)):
            path = path.substr(localRoot.length):
        if (path.startswith("/")):
            path = path.substr(1)
        return path;


    def on_dir_ok(self):
        def on_visit_remote_end():
            count = 0;
            for (var k in self.remote_files):
                if (self.remote_files.hasOwnProperty(k)):
                    ++count;
            def on_visit_local_end():
                def on_local_handle_end():
                    def on_remote_handle_end():
                        self.exit();
                    self.handle_remote_items(self.remote_files_stack.shift(), on_remote_handle_end)
                self.handle_local_items(self.local_files.shift(), on_local_handle_end)

            self.visit_local(settingsHelper.getNotePath(),on_visit_local_end)
        self.visit_remote(self.nextcloudRoot, on_visit_remote_end);


    def upload_and_save(self, local_db_item, callback):
        print("uploading: "+local_db_item.path)
        if(local_db_item['type'] == "directory"):

        else:
            self.client.upload_sync(self.nextcloud_root + "/" + local_db_item.path, local_db_item.path)



Sync.prototype.uploadAndSave = function (local_db_item, callback) {
    console.logDebug("uploading " + local_db_item.path)
    var sync = this;
    if (local_db_item.type === "directory") {
        console.logDebug("mkdir")
        this.client.createDirectory(this.nextcloudRoot + "/" + local_db_item.path).then(function () {
            sync.client.stat(sync.nextcloudRoot + "/" + local_db_item.path).then(function (stat) {
                DBItem.fromNC(sync.nextcloudRoot, stat)
                sync.save(local_db_item, DBItem.fromNC(sync.nextcloudRoot, stat))
                console.logDebug(JSON.stringify(stat, undefined, 4));
                callback()
            }).catch(function (err) {
                console.logDebug(err);
                sync.exit();
            });
        })

    } else {
        var data = this.fs.readFileSync(this.settingsHelper.getNotePath() + "/" + local_db_item.path);

        this.client.putFileContents(this.nextcloudRoot + "/" + local_db_item.path, data, { format: "binary" }).then(function (contents) {

            sync.client.stat(sync.nextcloudRoot + "/" + local_db_item.path).then(function (stat) {
                DBItem.fromNC(sync.nextcloudRoot, stat)
                sync.save(local_db_item, DBItem.fromNC(sync.nextcloudRoot, stat))
                console.logDebug(JSON.stringify(stat, undefined, 4));
                callback()
            }).catch(function (err) {
                console.logDebug(err);
                sync.exit();
            });
        });
    }
}


    def save(self, local, remote):
        local.remotelastmod = remote.remotelastmod
        self.db[local.path] = local
        self.saveDB()


    def saveDB(self):
        file = open('db.json', 'w')
        file.write(json.dumps(self.db))
        file.close()

    def download_and_save(self, remote_db_item, callback) {
        print("downloading " + remote_db_item.path)
        fpath = settingsHelper.getNotePath() + "/" + remote_db_item.path
        if (remote_db_item.type === "directory"):
            try:
                os.makedirs(fpath)
                if (success):
                    const stat = sync.fs.statSync(fpath)
                    sync.save(DBItem.fromFS(sync.settingsHelper.getNotePath(), fpath, stat), remote_db_item)
                    sync.hasDownloadedSmt = true;
                    callback();
            except Error:
                print("error")
                self.exit()


        else:
            try:
                self.client.download_sync(self.nextcloud_root + "/" + remote_db_item.path, fpath)
                stat = os.stat(fpath)
                sync.save(DBItem(sync.settingsHelper.getNotePath(), fpath, stat), remote_db_item)
                self.has_downloaded_smt = True;
                callback();
            except Error:
                print("Error downloading "+remote_db_Item.path);
                self.exit();

    def exit(self):
        self.is_syncing = False
        print("exit")
        if(self.is_full_sync):
            print("setting sync to 10 minutes")

        self.on_sync_end(self.has_download_smt)
        if (this.syncNext.length > 0):
            to_sync = this.syncNext.pop();
            self.syncOneItem(to_sync.path, to_sync.callback)

    def deleteLocalAndSave(self, local, callback):
        if (local.type === "directory"):
            print("delete dir later")
            self.local_dir_to_rm.append(local)
            callback()
        else:
            print("delete " + settingsHelper.getNotePath() + "/" + local.path)
            os.remove(this.settingsHelper.getNotePath() + "/" + local.path)
            del self.db[local.path];
            self.saveDB()


    def handle_remote_items(self, remote_db_Item, callback):
        if (remote_db_item == None):
            callback()
            return
        print("handle_remote_items")
        def cb ():
             self.handle_remote_items(self.remote_files_stack.pop(0), callback)

        in_db_item = sync.db[remote_db_item.path];
        if (in_db_item === None):
            #download
            self.download_and_save(remote_db_item, cb)
        else:
            if (in_db_item.remotelastmod === remote_db_Item.remotelastmod):
                #delete remote
                self.delete_remote_and_save(remote_db_item, cb)
            else:
                self.download_and_save(remote_db_item, cb)

    def deleteRemoteAndSave(self, remote, callback) {
        print("delete remote " + remote.path)
        if (remote.type === "directory"):
            self.remote_dir_to_rm.append(remote)
            callback()
        else:
            try:
                self.client.clean(self.nextcloud_root + "/" + remote.path)
            except Error:
                sync.exit()



    def handle_local_items(self, local_db_item, callback):
        if (local_db_item == None):
            callback()
            return False
        in_db_item = self.db[local_db_item.path];
        print(local_db_item.path)
        var sync = this;
        var inDBItem = sync.db[local_db_item.path];
        var remote_db_item = self.remote_files[local_db_item.path];
        if (remote_db_item != None):
            del self.remote_files_stack[self.remote_files_stack.indexof(remote_db_item), 1];
        def cb1():
            self.handle_local_items(sync.localFiles.pop(0), callback)

        cb = cb1
        if (in_db_item == None): #has never been synced
            if (remote_db_item == None): #is not on server
                #upload  and save
                print("not on server")
                self.upload_and_save(local_db_item, cb)
            else: #is on server
                if (remote_db_item.remotelastmod !== local_db_item.locallastmod):
                    #conflict
                    if (local_db_item.type !== "directory"):
                        print("conflict on " + local_db_item.path)
                        self.fix_conflict(local_db_item, remote_db_item, cb)
                    else:
                        cb()

                else:
                    #that's ok !
                    print("OK 1 ")
                    self.save(local_db_item, remote_db_item, cb)
        else: #has already been synced
            if (remote_db_item == None): #is not on server
                if (local_db_item.locallastmod === inDBItem.locallastmod): # was already sent
                    #delete local...
                    self.delete_local_and_save(local_db_item, cb)
                else:
                    #upload
                    print("not up to date on server")
                    self.upload_and_save(local_db_item, cb)
            else: #is on server
                if (remote_db_item.remotelastmod === inDBItem.remotelastmod):
                    if (local_db_item.locallastmod === inDBItem.locallastmod):
                        print("nothing to do !")
                        cb();
                    else:
                        #upload
                        if (inDBItem.type !== "directory"):
                            sync.upload_and_save(local_db_item, cb)
                        else cb()
                else if (local_db_item.locallastmod === inDBItem.locallastmod):
                    #download
                    if (local_db_item.type !== "directory"):
                        self.download_and_save(remote_db_item, cb)

                else:
                    #conflict

                    if (local_db_item.type !== "directory"):
                        print("conflict on " + local_db_item.path)
                        self.fix_conflict(local_db_item, remote_db_item, cb)
                    else cb()


    def fix_conflict(self, local_db_item, remote_db_item, callback):
        fpath = tempfile.gettempdir()+"/tmpconflictfix.sqd"
        self.client.download_sync(self.nextcloud_root + "/" + remote_db_item.path, fpath)
        if(filecmp.cmp(fpath, local_db_item.path, shallow=False)):
            #fixed
            os.remove(fpath)
            self.save(local_db_item, remote_db_item)
            callback();
        else:
            print("real conflict... fixing")
            split_name = os.path.splitext(local_db_item.path)
            new_name = split_name[0]+" conflit "+date
            if(len(split_name)>1):
                new_name += split_name[1]
            os.rename(local_db_item.path, os.path.join(os.path.dirname(local_db_item.path),new_name))
            os.rename(fpath,local_db_item.path)
            sync.save(local_db_item, remote_db_item)
            callback()
    def visit_local(self, path, callback):
        for root, dirs, files in os.walk(path, topdown=False):
           for name in files:
              self.local_files.append(DBFile.from_fs(Sync.correct_local_path(settingsManager.getNotePath(),os.path.join(root, name)), os.stat(os.path.join(root, name)))
           for name in dirs:
              self.local_files.append(DBFile.from_fs(Sync.correct_local_path(settingsManager.getNotePath(),os.path.join(root, name)), os.stat(os.path.join(root, name)))


Sync.prototype.visitRemote = function (path, callback) {
    var sync = this;
    this.client
        .getDirectoryContents(path)
        .then(function (contents) {
            for (var i of contents) {
                var item = DBItem.fromNC(sync.nextcloudRoot, i)
                /*if (this.db[item.path] !== undefined && this.db[item.path].remotelastmod === item.remotelastmod){

                }*/
                sync.remoteFiles[item.path] = item;
                sync.remoteFilesStack.push(item)
                if (item.type == "directory")
                    sync.remoteFoldersToVisit.push(i.filename)
                // console.logDebug(correctPath(sync.nextcloudRoot, i.filename));
            }
            // console.logDebug("sync.remoteFoldersToVisit.length " + sync.remoteFoldersToVisit.length)
            if (sync.remoteFoldersToVisit.length !== 0) {
                sync.visitRemote(sync.remoteFoldersToVisit.pop(), callback)
            } else
                callback()
        }).catch(function (err) {
            console.logDebug(err);
            sync.exit();
        });
}


class DBItem():
    def __init__(self, path, locallastmod, remotelastmod, type):
        self.path = path
        self.locallastmod = locallastmod
        self.remotelastmod = remotelastmod
        self.type=type

    def from_nc(ncroot, ncitem):
        return DBItem()

    def from_fs(path, stat):
        return DBItem(path, stat.st_mtime, S_ISDIR(stat.st_mode) ? "file" : "directory"
