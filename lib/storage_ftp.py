from config import Config


class FTP(object):
    """
        http://designerror.github.io/webdav-client-python/
    """
    def __init__(self, config):
        if not isinstance(config, Config):
            raise Exception('InvalidConfigException')

        self._config = config
        self._logger = config.logger

    def run(self, filepath):
        self._logger.info('storage FTP/SFTP, file: {0}'.format(filepath))
