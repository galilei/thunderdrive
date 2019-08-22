# -*- coding: utf8 -*-
import os

class ThunderDriveFSLike():
  def __init__(self, adapter):
    self.adapter = adapter

  def remove(self, path):
    self.adapter.remove(path)

  def walk(self, top='/', topdown=True, onerror=None, followlinks=False):
    if top == '/':
      top = [{
        'name': '/',
        'hash': 'root'
      }]

    dirs = []
    nondirs = []
    for entity in self.adapter.getEntities(top[-1]['hash']):
      if entity['type'] == 'folder':
        dirs.append(entity)
      else:
        nondirs.append(entity)

    if topdown:
      yield top, dirs, nondirs

    for directory in dirs:
      for x in self.walk(top + [directory], topdown, onerror, followlinks):
        yield x

    if not topdown:
      yield top, dirs, nondirs

if __name__ == "__main__":
    dircount = 0
    filecount = 0
    # └

    from adapter import ThunderDriveAdapter
    adapter = ThunderDriveAdapter(os.environ['EMAIL'], os.environ['PASSWORD'])

    tdfs = ThunderDriveFSLike(adapter);
    for fullpath, dirs, files in tdfs.walk('/'):
      depth = len(fullpath) - 1

      base_str_to_print = ''
      str_to_print = ''
      if depth > 0:
        if depth > 1:
          spaces_size = reduce(lambda x, y: x+y, map(lambda x: len(x['name']) + 1, fullpath[:-2])) - 1
          base_str_to_print = '│' + (' ' * spaces_size)

        dash_size = len(fullpath[-2]['name']) - 1
        str_to_print = base_str_to_print + '├' + ('─' * dash_size)
        str_to_print = str_to_print + ' '

      print(str_to_print + fullpath[-1]['name'].encode('utf8'))

      base_str_to_print = base_str_to_print + (' ' * (len(fullpath[-1]['name']) + 1))
      file_dash_size = len(fullpath[-1]['name'])
      for file in files:
        print(base_str_to_print + '├' + ('─' * file_dash_size) + file['name'].encode('utf8'))
      # print map(lambda x:x['name'], fullpath)
      # print map(lambda x:x['name'], dirs)
      # print map(lambda x:x['name'], files)
      # print "============================"
