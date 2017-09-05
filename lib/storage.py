import os
from app import App
from storage_webdav import WebDAV
from storage_rest import REST
from storage_ftp import FTP


class Storage(object):
    """
    https://pypi.python.org/pypi/webdavclient
    https://tech.yandex.ru/disk/rest/
    https://github.com/Hixon10/simple-rest-yandex-disk-client
    """
    def __init__(self, app, filepath):
        if not isinstance(app, App):
            raise Exception('InvalidConfigException')

        self._app = app

        if not os.path.exists(filepath):
            raise IOError('Attach file not found at: {0}, exit'.format(os.path.abspath(filepath)))
        self._filepath = os.path.abspath(filepath)

    def run(self):
        getattr(self, 'sync_{}'.format(self._app.config.storage_transport))(self._filepath)

    def sync_webdav(self, filepath):
        WebDAV(self._app).run(filepath)

    def sync_rest(self, filepath):
        REST(self._app).run(filepath)

    def sync_ftp(self, filepath):
        FTP(self._app).run(filepath)
