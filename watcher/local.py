
# -*- coding: utf8 -*-
from watchdog.events import FileSystemEventHandler, DirModifiedEvent

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, queue):
      self.queue = queue

    def on_created(self, event):
      print('on_created', event)
      self.queue.put({
          'name': 'sync',
          'path': event.src_path
        })

    def on_deleted(self, event):
        print('on_deleted', event)
        self.queue.put({
          'name': 'delete',
          'path': event.src_path
        })

    def on_modified(self, event):
      print('on_modified', event)
      if type(event) is not DirModifiedEvent:
        print('adding to queue')
        self.queue.put({
          'name': 'sync',
          'path': event.src_path
        })

    def on_moved(self, event):
        print('on_moved', event)
        self.queue.put({
          'name': 'move',
          'src': event.src_path,
          'dst': event.dst_path
        })
