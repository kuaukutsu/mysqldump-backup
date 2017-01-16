import os
import config as cfg
from utils import encrypt, program_popen
from fnmatch import fnmatch


class Mysqldump(object):
    def __init__(self, config):
        if not isinstance(config, cfg.Config):
            raise Exception('InvalidConfigException')
        self._config = config

    def run(self):
        self._config.logger.info('mysqldump run')

        self.watch()
        self.dump()

        # encryption
        if self.__use_encrypt():
            self._config.logger.info('use encrypt')
            encrypt(self.__filepath(),
                    self.__filepath_encrypt(),
                    self._config.encrypt_pass,
                    self._config.compress_level)

        return self.__filepath_encrypt() if self.__use_encrypt() else self.__filepath()

    def dump(self):
        # build command
        cmd = self.__create_cmd()
        self._config.logger.debug('{0}'.format(cmd))

        # clean
        filepath = self.__filepath()
        if os.path.exists(filepath):
            # overide? vote?
            os.remove(filepath)
        # exec command
        program_popen(cmd)

    def watch(self):
        work_dir = self._config.save_filepath
        max_copies_count = self._config.max_copies_count
        files = [f for f in os.listdir(work_dir)
                 if os.path.isfile(os.path.join(work_dir, f)) and fnmatch(f, self._config.save_filename_mask)]

        # sort ctime
        files.sort(key=lambda fn: os.path.getmtime(os.path.join(work_dir, fn)))

        # remove old copies
        if 0 < max_copies_count <= len(files):
            for f in files[0:(len(files) - max_copies_count)]:
                self._config.logger.debug('remove old copies {0}'.format(f))
                os.remove(os.path.join(work_dir, f))

    def __create_cmd(self):
        # config
        config = self._config

        return 'mysqldump{host}{user}{password}{options}{database}{gzip} > {filepath}'.format(
            host=' -h ' + config.db_host if config.db_host else '',
            port=' -P ' + config.db_port if config.db_port else '',
            user=' -u ' + config.db_user if config.db_user else '',
            password=' -p' + config.db_pass if config.db_pass else '',
            database=' -B ' + config.database if config.database else '',
            options=' ' + config.db_options if config.db_options else '',
            gzip=' | gzip ' if self.__use_gzip() else '',
            filepath=self.__filepath()
        )

    def __use_encrypt(self):
        return self._config.is_encrypt

    def __use_gzip(self):
        return self._config.is_gzip and not self.__use_encrypt()

    def __filepath(self):
        return os.path.join(self._config.save_filepath,
                            self._config.save_filename.format(ext='sql.gz' if self.__use_gzip() else 'sql'))

    def __filepath_encrypt(self):
        return os.path.join(self._config.save_filepath,
                            self._config.save_filename.format(ext='zip'))
