# -*- coding: utf8 -*-
import requests
import os
import urllib
import json
import base64
from anytree import Node, Resolver, RenderTree
from anytree.resolver import ChildResolverError

import logging
logger = logging.getLogger(__name__)

class ThunderDriveAdapter():
  HOST = 'https://app.thunderdrive.io'

  def __init__(self, email, password):
    self.cookies = requests.cookies.RequestsCookieJar()
    self.user_config = None
    self.email = email
    self.password = password
    self.headers = {
      'Origin': '%s' % (self.HOST),
      'Referer': '%s/drive' % (self.HOST)
    }

  def authenticated(func):
    def require_login(*args, **kwargs):
      self = args[0]
      if self.user_config == None:
        self.login()
      return func(*args, **kwargs)
      # TODO: Support re-login when deauthenticated
    return require_login

  def login(self):
    logger.info('Logging in to Thunder Drive')
    r = requests.post('%s/secure/auth/login' % (self.HOST), json = {
      "remember": True,
      "password": self.password,
      "email": self.email
      }, headers = self.headers, allow_redirects = False)

    if r.status_code == 200:
      response = r.json()
      if response['status'] == 'success':
        self.cookies = r.cookies
        self.user_config = json.loads(base64.decodestring(response['data']))

  @authenticated
  def getEntities(self, folder_id='root', order_by='updated_at', order_dir='desc'):
    logger.info('Getting entities')
    r = requests.get('%s/secure/drive/entries' % (self.HOST), params = {
      'orderBy': order_by,
      'orderDir': order_dir,
      'folderId': folder_id
    }, cookies = self.cookies, headers = self.headers, allow_redirects = False)
    if r.status_code == 200:
      return r.json()['data']
    if r.is_redirect and r.headers['Location'].endswith('/login'):
      self.login()
    return []

  @authenticated
  def stat(self, path):
    logger.info('Getting file details (%s)', path)
    path = '/root/' + path

    folders_tree = self.folders()
    resolver = Resolver('name')

    try:
      return resolver.get(folders_tree, path).data
    except ChildResolverError:
      pass

    dir_node = resolver.get(folders_tree, os.path.dirname(path))
    for entity in self.getEntities(dir_node.data['hash']):
      if entity['name'] == os.path.basename(path):
        return entity

  @authenticated
  def remove(self, path):
    logger.info('Removing %s', path)

    stat = self.stat(path)
    if stat is not None:
      r = requests.post('%s/secure/drive/entries' % (self.HOST), json = {
        '_method': 'DELETE',
        'entryIds': [
          stat['id']
        ]
      }, cookies = self.cookies, headers = {'X-XSRF-TOKEN': urllib.unquote(self.cookies.get('XSRF-TOKEN'))}, allow_redirects = False)
      if r.status_code == 200:
        logger.info('Successfully removed %s', path)
        return True
    logger.warning('Could not remove %s', path)
    return False

  @authenticated
  def folders(self):
    logger.info('Getting folders')

    r = requests.get('%s/secure/drive/users/%s/folders' % (self.HOST, self.user_config['user']['id']), cookies = self.cookies, headers = self.headers, allow_redirects = False)
    if r.status_code == 200:
      folder_by_id = {}
      root = Node('root')

      for folder in r.json()['folders']:
        parent = root
        parent_id = folder['parent_id']
        if folder_by_id.has_key(parent_id):
          parent = folder_by_id[parent_id]
        folder_by_id[folder['id']] = Node(folder['name'], parent=parent, data=folder)

      for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))
      return root

  @authenticated
  def space_usage(self):
    logger.info('Getting space usage')

    r = requests.get('%s/secure/drive/user/space-usage' % (self.HOST), cookies = self.cookies, headers = self.headers, allow_redirects = False)
    if r.status_code == 200:
      print(r.json())

  @authenticated
  def upload(self, path, filepath):
    logger.info('Uploading file (%s, %s)', path, filepath)

    files = { }
    files['parentId'] = (None, '')
    files['file'] = (os.path.basename(filepath), open(filepath, 'rb'), 'application/octet-stream')
    files['path'] = (None, path)

    from requests_toolbelt import MultipartEncoder
    m = MultipartEncoder(files, boundary='----WebKitFormBoundaryoruGlidzF7cLzcCl')

    r = requests.post('%s/secure/uploads' % (self.HOST), data = m.to_string(), cookies = self.cookies, headers = {'Content-Type': m.content_type, 'X-XSRF-TOKEN': urllib.unquote(self.cookies.get('XSRF-TOKEN'))}, allow_redirects = False)
    if r.status_code == 200:
      pass
