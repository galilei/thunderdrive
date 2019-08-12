import sys
import time
import requests
import jwt
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


import logging

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class ThunderDriveAdapter():
  HOST = 'https://app.thunderdrive.io'
  # HOST = 'http://localhost:12345'
  def __init__(self):
    self.cookies = requests.cookies.RequestsCookieJar()
    self.user_id = ''
    self.headers = {
      'Origin': '%s' % (self.HOST),
      'Referer': '%s/drive' % (self.HOST)
    }

  def login(self):
    r = requests.post('%s/secure/auth/login' % (self.HOST), json = {
      "remember": True,
      "password": "",
      "email": ""
      }, headers = self.headers)

    if r.status_code == 200:
      response = r.json()
      if response['status'] == 'success':
        self.cookies = r.cookies
        self.token = response['data']

  def getEntities(self):
    r = requests.get('%s/secure/drive/entries?orderBy=updated_at&orderDir=desc&folderId=root' % (self.HOST), data = {
      'orderBy': 'updated_at',
      'orderDir': 'desc',
      'folderId': 'root'
    }, cookies = self.cookies, headers = self.headers)
    if r.status_code == 200:
      pass

  def getFolders(self):
    r = requests.get('%s/secure/drive/users/%s/folders' % (self.HOST, self.user_id), cookies = self.cookies, headers = self.headers)
    if r.status_code == 200:
      pass

  def upload(self, path, filepath):
    files = { }
    files['parentId'] = (None, '')
    files['file'] = (os.path.basename(filepath), open(filepath, 'rb'), 'application/octet-stream')
    files['path'] = (None, path)

    from requests_toolbelt import MultipartEncoder
    m = MultipartEncoder(files, boundary='----WebKitFormBoundaryoruGlidzF7cLzcCl')


    r = requests.post('%s/secure/uploads' % (self.HOST), data = m.to_string(), cookies = self.cookies, headers = {'Content-Type': m.content_type})
    if r.status_code == 200:
      pass

class ImagesEventHandler(FileSystemEventHandler):
    def on_created(self, event):
      print('on_created', event)
      self.process(event)

    def on_deleted(self, event):
        print('on_deleted', event)
        self.process(event)

    def on_modified(self, event):
        print('on_modified', event)
        self.process(event)

    def on_moved(self, event):
        print('on_moved', event)
        self.process(event)

    def process(self, event):
        # filename, ext = os.path.splitext(event.src_path)
        # filename = f"{filename}_thumbnail.jpg"
#
        # image = Image.open(event.src_path)
        # image = grayscale(image)
        # image.thumbnail(self.THUMBNAIL_SIZE)
        # image.save(filename)
        pass

class ImagesWatcher:
    def __init__(self, src_path):
        self.__src_path = src_path
        self.__event_handler = ImagesEventHandler()
        self.__event_observer = Observer()

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()

    def __schedule(self):
        self.__event_observer.schedule(
            self.__event_handler,
            self.__src_path,
            recursive=True
        )

if __name__ == "__main__":
    # src_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    # ImagesWatcher(src_path).run()
    thunderdrive = ThunderDriveAdapter()
    thunderdrive.login()
    # thunderdrive.getEntities()
    thunderdrive.upload('/test', '/home/romeupalos/Documents/Gru/romeu2')
