from app import App


class REST(object):
    """
        http://designerror.github.io/webdav-client-python/
    """
    def __init__(self, app):
        if not isinstance(app, App):
            raise Exception('InvalidConfigException')

        self._config = app.config
        self._logger = app.logger

    def run(self, filepath):
        self._logger.info('storage REST, file: {0}'.format(filepath))
