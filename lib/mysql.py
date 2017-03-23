import os
from config import Config
from utils import encrypt, program_popen
from fnmatch import fnmatch


class Mysqldump(object):
    def __init__(self, config):
        if not isinstance(config, Config):
            raise Exception('InvalidConfigException')
        self._config = config
        self._logger = config.logger

    def run(self):
        self._logger.info('mysqldump run')
        # clean
        self.watch()
        # save filepath
        self.dump()
        # encrypt
        if self.__use_encrypt():
            self._logger.info('use encrypt')
            encrypt(self.__filepath(),
                    self.__filepath_encrypt(),
                    self._config.encrypt_pass,
                    self._config.compress_level)
            return self.__filepath_encrypt()

        return self.__filepath()

    def dump(self):
        # clean exists
        if os.path.exists(self.__filepath()):
            os.remove(self.__filepath())

        cmd = self.__create_cmd()
        self._logger.debug(cmd)
        # exec command
        program_popen(cmd)

    def watch(self):
        work_dir = self._config.save_filepath
        # list files
        files = [f for f in os.listdir(work_dir)
                 if os.path.isfile(os.path.join(work_dir, f)) and fnmatch(f, self._config.save_filename_mask)]

        # sort ctime
        files.sort(key=lambda fn: os.path.getmtime(os.path.join(work_dir, fn)))

        # remove old copies
        if 0 < self._config.max_copies <= len(files):
            for f in files[0:(len(files) - self._config.max_copies)]:
                self._logger.debug('remove old copies {0}'.format(f))
                os.remove(os.path.join(work_dir, f))

    def __create_cmd(self):
        return 'mysqldump{host}{user}{password}{options}{database}{gzip} > {filepath}'.format(
            host=' -h ' + self._config.db_host if self._config.db_host else '',
            port=' -P ' + self._config.db_port if self._config.db_port else '',
            user=' -u ' + self._config.db_user if self._config.db_user else '',
            password=' -p' + self._config.db_pass if self._config.db_pass else '',
            database=' -B ' + self._config.database if self._config.database else '',
            options=' ' + self._config.db_options if self._config.db_options else '',
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
