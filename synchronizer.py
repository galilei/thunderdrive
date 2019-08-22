import os
from Queue import Empty
from threading import Thread

import logging
logger = logging.getLogger(__name__)

class Synchronizer(Thread):
  def __init__(self, rootpath, queue, thunderdrive_adapter):
    Thread.__init__(self)
    self.queue = queue
    self.rootpath = rootpath
    self.thunderdrive_adapter = thunderdrive_adapter
    self.running = True

  def _remove_prefix(self, string):
    return string[len(self.rootpath):]

  def stop(self):
    self.running = False

  def run(self):
    while self.running:
      try:
        event = self.queue.get(True, 0.1)
        logger.debug('Event received', event)

        if event['name'] == 'sync':
          dst_folder = os.path.dirname(self._remove_prefix(event['path']))
          # print(dst_folder, event['path'])
          self.thunderdrive_adapter.upload(dst_folder, event['path'])

        elif event['name'] == 'delete':
          path = self._remove_prefix(event['path'])
          self.thunderdrive_adapter.remove(path)

        self.queue.task_done()
      except Empty as e:
        pass
      except Exception as e:
        logger.error('An error occurred %s', exc_info=True)

