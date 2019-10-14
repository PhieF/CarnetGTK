import webdav.client as wc
from .settings_manager import *
import pycurl
import lxml.etree as etree
from io import BytesIO
from re import sub
from webdav import *
from webdav.exceptions import *
from webdav.urn import Urn
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

class MyUrn(Urn):
    def __init__(self, hree, etag):
        super(MyUrn, self).__init__(hree)
        self.etag = etag

    def get_etag(self):
        return self.etag

class Sync():

    def __init__(self):
        options = {
            'webdav_hostname': "https://carnet.live/remote.php/webdav/",
            'webdav_login':    "Phoenamandre",
            'webdav_password': "Wi2fvr00?!"
        }
        self.client = wc.Client(options)

        paths = self.list('/')

        for remote_resource_name in paths:
            print(remote_resource_name.get_etag())


    def list(self, remote_path="/"):
        def parse(response):

            try:
                response_str = response.getvalue()
                print(response_str)
                tree = etree.fromstring(response_str)
                hrees = [unquote(hree.text) for hree in tree.findall(".//{DAV:}href")]
                etags = [unquote(etag.text) for etag in tree.findall(".//{DAV:}getetag")]
                i=0
                ret = []
                for hree in hrees:
                    ret.append(MyUrn(hree, etags[i]))
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

            url = {'hostname': self.client.webdav.hostname, 'root': self.client.webdav.root, 'path': directory_urn.quote()}
            options = {
                'URL': "{hostname}{root}{path}".format(**url),
                'CUSTOMREQUEST': wc.Client.requests['list'],
                'HTTPHEADER': self.client.get_header('list'),
                'WRITEDATA': response,
                'NOBODY': 0
            }

            request = self.client.Request(options=options)

            request.perform()
            request.close()

            urns = parse(response)

            #path = "{root}{path}".format(root=self.client.webdav.root, path=directory_urn.path())
            #return [urn.filename() for urn in urns if urn.path() != path and urn.path() != path[:-1]]
            return urns

        except pycurl.error:
            raise NotConnection(self.client.webdav.hostname)




    def push(self, remote_directory, local_directory):

        def prune(src, exp):
            return [sub(exp, "", item) for item in src]

        urn = Urn(remote_directory, directory=True)

        if not self.is_dir(urn.path()):
            raise OptionNotValid(name="remote_path", value=remote_directory)

        if not os.path.isdir(local_directory):
            raise OptionNotValid(name="local_path", value=local_directory)

        if not os.path.exists(local_directory):
            raise LocalResourceNotFound(local_directory)

        paths = self.list(urn.path())
        expression = "{begin}{end}".format(begin="^", end=urn.path())
        remote_resource_names = prune(paths, expression)

        for local_resource_name in listdir(local_directory):

            local_path = os.path.join(local_directory, local_resource_name)
            remote_path = "{remote_directory}{resource_name}".format(remote_directory=urn.path(), resource_name=local_resource_name)

            if os.path.isdir(local_path):
                if not self.check(remote_path=remote_path):
                    self.mkdir(remote_path=remote_path)
                self.push(remote_directory=remote_path, local_directory=local_path)
            else:
                if local_resource_name in remote_resource_names:
                    s = os.stat(local_path)
                    try:
                        db_item = self.db[self.get_relative_local_path(local_path)]

                    except KeyError:
                        db_item = None
                    if(db_item == None or db_item['locallastmod'] != s.st_mtime):
                        print("pet")

                self.upload_file(remote_path=remote_path, local_path=local_path)

    def pull(self, remote_directory, local_directory):

        def prune(src, exp):
            return [sub(exp, "", item) for item in src]

        urn = Urn(remote_directory, directory=True)

        if not self.is_dir(urn.path()):
            raise OptionNotValid(name="remote_path", value=remote_directory)

        if not os.path.exists(local_directory):
            raise LocalResourceNotFound(local_directory)

        local_resource_names = listdir(local_directory)

        paths = self.list(urn.path())
        expression = "{begin}{end}".format(begin="^", end=remote_directory)
        remote_resource_names = prune(paths, expression)

        for remote_resource_name in remote_resource_names:

            local_path = os.path.join(local_directory, remote_resource_name)
            remote_path = "{remote_directory}{resource_name}".format(remote_directory=urn.path(), resource_name=remote_resource_name)

            remote_urn = Urn(remote_path)

            if self.is_dir(remote_urn.path()):
                if not os.path.exists(local_path):
                    os.mkdir(local_path)
                self.pull(remote_directory=remote_path, local_directory=local_path)
            else:
                if remote_resource_name in local_resource_names:
                    continue
                self.download_file(remote_path=remote_path, local_path=local_path)

    def sync(self, remote_directory, local_directory):

        self.pull(remote_directory=remote_directory, local_directory=local_directory)
        self.push(remote_directory=remote_directory, local_directory=local_directory)
