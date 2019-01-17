from os import path
from app import App


class WebDAV(object):
    """
        http://designerror.github.io/webdav-client-python/
    """
    def __init__(self, app):
        if not isinstance(app, App):
            raise Exception('InvalidConfigException')

        self._config = app.config
        self._logger = app.logger

    def run(self, filepath):
        self._logger.info('storage WebDAV, file: {0}'.format(filepath))

        options = {
            'webdav_hostname': self._config.storage_host,
            'webdav_login': self._config.storage_user,
            'webdav_password': self._config.storage_pass,
            'verbose': True if self._config.is_debug else False
        }

        # ext option
        if self._config.storage_proxy_host:
            options['proxy_hostname'] = self._config.storage_proxy_host
        if self._config.storage_proxy_user:
            options['proxy_login'] = self._config.storage_proxy_user
        if self._config.storage_proxy_pass:
            options['proxy_password'] = self._config.storage_proxy_pass
        if self._config.storage_cert_path:
            options['cert_path'] = self._config.storage_cert_path
        if self._config.storage_key_path:
            options['key_path'] = self._config.storage_key_path

        # client = wc.Client(options)
        # # need check authorized
        # if not client.check(self._config.storage_dir):
        #     self._logger.info('path {0} not exists'.format(self._config.storage_dir))
        #     client.mkdir(self._config.storage_dir)
        #
        # # remove old copies
        # files = client.list(self._config.storage_dir)
        # if 0 < self._config.storage_max_copies <= len(files):
        #     files.sort(reverse=False)
        #     for f in files[0:(len(files) - self._config.storage_max_copies)]:
        #         self._logger.debug('remove old copies {0}'.format(f))
        #         client.clean(path.join(self._config.storage_dir, f))
        #
        # # upload
        # client.upload_file(remote_path=path.join(self._config.storage_dir, path.basename(filepath)),
        #                    local_path=filepath)
