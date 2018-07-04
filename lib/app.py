# !/usr/bin/env python
import os
import logging
from utils import Singleton
from config import Config

CONFIG_FILE = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/mysqldump.cfg'


# application
class App(object):
    __metaclass__ = Singleton

    def __init__(self):

        # parse configurations
        self._config = Config(CONFIG_FILE)

        # init logger
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                            datefmt='%Y/%m/%d %H:%M:%S',
                            level=logging.DEBUG if self._config.is_debug else logging.WARNING)
        self._logger = logging.getLogger(__name__)

        # handler log
        if self._config.logfile:
            handler = logging.FileHandler(self._config.logfile)
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y/%m/%d %H:%M:%S')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    @property
    def config(self):
        return self._config

    @property
    def logger(self):
        return self._logger
