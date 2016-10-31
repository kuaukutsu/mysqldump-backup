import os
import config as cfg
from fnmatch import fnmatch


class Storage(object):
    """
    https://pypi.python.org/pypi/webdavclient
    https://tech.yandex.ru/disk/rest/
    https://github.com/Hixon10/simple-rest-yandex-disk-client
    """
    def __init__(self, config, filepath):
        if not isinstance(config, cfg.Config):
            raise Exception('InvalidConfigException')
        self._config = config

        if not os.path.exists(filepath):
            raise IOError('Attach file not found at: {0}, exit'.format(os.path.abspath(filepath)))
        self._filepath = os.path.abspath(filepath)

    def run(self):
        self.watch()

    def watch(self):
        work_dir = self._config.webdav_dir
        max_copies_count = self._config.webdav_max_copies_count
