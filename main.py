# -*- coding: utf8 -*-

import time
import os
import logging
from watchdog.observers import Observer
from Queue import Queue
from synchronizer import Synchronizer

from thunderdrive.adapter import ThunderDriveAdapter
from watcher.local import FileEventHandler

import logging
logger = logging.getLogger(__name__)

# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


logger.info('Initializing')
queue = Queue()

folder = '/home/romeupalos/rep/github/thunderdrive/test'
watcher = FileEventHandler(queue)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
observer = Observer()
observer.schedule(watcher, folder, recursive=True)
observer.start()

adapter = ThunderDriveAdapter(os.environ['EMAIL'], os.environ['PASSWORD'])
adapter.space_usage()
sync = Synchronizer(folder, queue, adapter)
sync.start()
try:
  while True:
    time.sleep(0.1)
except KeyboardInterrupt:
  observer.stop()
  observer.join()
  print 'wait queue'
  queue.join()
  print 'wait queue done'
  sync.stop()
  sync.join()
