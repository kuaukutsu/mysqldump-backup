import os
import config as cfg
from fnmatch import fnmatch


class WebDAV(object):
    """
    https://pypi.python.org/pypi/webdavclient
    """
    def __init__(self, config):
        if not isinstance(config, cfg.Config):
            raise Exception('InvalidConfigException')
        self._config = config

    def run(self):
        self.watch()

    def watch(self):
        work_dir = ''
        max_copies_count = self._config.webdav_max_copies_count
        files = [f for f in os.listdir(work_dir)
                 if os.path.isfile(os.path.join(work_dir, f)) and fnmatch(f, self._config.save_filename_mask)]

        # sort ctime
        files.sort(key=lambda fn: os.path.getmtime(os.path.join(work_dir, fn)))

        # remove old copies
        if 0 < max_copies_count <= len(files):
            for f in files[0:(len(files) - max_copies_count)]:
                pass
