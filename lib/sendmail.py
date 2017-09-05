import os
import shutil
from app import App
from smtp import Smtp
from utils import split
from mailgun import Mailgun


class Sendmail(object):
    """
        https://docs.python.org/2/library/email-examples.html
    """
    def __init__(self, app, filepath):
        if not isinstance(app, App):
            raise Exception('InvalidConfigException')

        self._app = app

        if not os.path.exists(filepath):
            raise IOError('Attach file not found at: {0}, exit'.format(os.path.abspath(filepath)))
        self._filepath = os.path.abspath(filepath)

    def run(self):
        self._app.logger.info('sendmail run')

        filesize = os.path.getsize(self._filepath)
        self._app.logger.info('backup size {0}'.format(filesize))

        # limit size
        if 0 < self._app.config.email_limit_size_attach < filesize:
            raise Exception('InvalidConfigException')

        # split
        if 0 < self._app.config.email_chunk_max_size < filesize:
            # work directory
            dir_split = os.path.join(os.path.dirname(self._filepath), 'split')
            if not os.path.exists(dir_split):
                os.mkdir(dir_split)

            # 7z a -vSIZE
            split(self._filepath,
                  os.path.join(dir_split, os.path.basename(self._filepath)),
                  str(self._app.config.email_chunk_max_size) + 'b')

            for f in os.listdir(dir_split):
                if os.path.isfile(os.path.join(dir_split, f)):
                    filepath = os.path.join(dir_split, f)
                    getattr(self, 'send_{}'.format(self._app.config.email_transport))(filepath)
                    os.remove(filepath)

            # clear directory
            shutil.rmtree(dir_split)
        else:
            getattr(self, 'send_{}'.format(self._app.config.email_transport))(self._filepath)

    def send_smtp(self, filepath):
        Smtp(self._app).send(filepath)

    def send_api(self, filepath):
        Mailgun(self._app).send(filepath)
