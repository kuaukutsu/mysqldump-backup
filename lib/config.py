#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import logging
import argparse
from utils import Singleton
from configparser import RawConfigParser as ConfigParser

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')


class Config(object):
    __metaclass__ = Singleton

    def __init__(self, config):
        self._config_file = config
        self._logger = logging.getLogger(__name__)
        self._args = self.__parse_args()
        self._config = self.__parse_config()

    def __parse_args(self):
        parser = argparse.ArgumentParser(description="Usage: %prog [options] ")
        parser.add_argument("-c", "--config-file",
                            dest="config",
                            type=str,
                            help="path to the config file")
        parser.add_argument("-d", "--database",
                            dest="database",
                            help="mysql database or name patern mysql",
                            required=True)
        parser.add_argument("-u", "--username",
                            dest="username",
                            help="mysql username")
        parser.add_argument("-p", "--password",
                            dest="password",
                            help="mysql password")
        parser.add_argument("-o", "--output",
                            dest="output",
                            help="path to the output directory")
        parser.add_argument("-l", "--log",
                            dest="logfile",
                            help="path to the log file")
        parser.add_argument("-g", "--gzip",
                            dest="gzip",
                            action='store_true',
                            default=False,
                            help="gzip mysqldump")
        parser.add_argument("-e", "--encrypt",
                            dest="encrypt",
                            action='store_true',
                            default=False,
                            help="encrypt mysqldump with zlib")
        parser.add_argument("--encrypt-pass",
                            dest="encrypt_pass",
                            type=str,
                            help="use with --encrypt, automatically turn --encrypt on and --gzip off")
        parser.add_argument("--compress-level",
                            dest="compress_level",
                            type=int,
                            default=6,
                            help="use with --encrypt")
        parser.add_argument("--webdav",
                            dest="webdav",
                            type=str,
                            help="copy mysqldump to Nameserver (WebDAV)")
        parser.add_argument("--sendmail",
                            dest="sendmail",
                            type=str,
                            help="send email")
        parser.add_argument("--options",
                            dest="options",
                            type=str,
                            help="options for mysqldump")
        parser.add_argument("--log-level",
                            dest="loglevel",
                            type=str,
                            help="default ERROR & CRITICAL, set --log-level=info,debug")

        args = parser.parse_args()
        if args.logfile:
            # create
            dirlog = os.path.dirname(args.logfile)
            if not os.path.exists(dirlog):
                os.makedirs(dirlog)

            # level
            handler = logging.FileHandler(args.logfile)
            if args.loglevel:
                if 'info' in args.loglevel.lower():
                    self._logger.setLevel(logging.INFO)
                    handler.setLevel(logging.INFO)
                if 'debug' in args.loglevel.lower():
                    self._logger.setLevel(logging.DEBUG)
                    handler.setLevel(logging.DEBUG)

            # format
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y/%m/%d %H:%M:%S')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

        if args.loglevel:
            if 'info' in args.loglevel.lower():
                self._logger.setLevel(logging.INFO)
            if 'debug' in args.loglevel.lower():
                self._logger.setLevel(logging.DEBUG)

        if args.encrypt_pass:
            self._logger.info('encrypt_pass is True')
            args.gzip = False
            args.encrypt = True

        if args.config:
            self._logger.info('use configuration {0}'.format(self._config_file))
            self._config_file = os.path.abspath(args.config)

        return args

    def __parse_config(self):
        parser = ConfigParser()
        if not os.path.exists(self._config_file):
            self._logger.error('Config file not found at: {0}, exit'.format(os.path.abspath(self._config_file)))
            raise IOError('Config file not found at: {0}, exit'.format(os.path.abspath(self._config_file)))
        parser.read(self._config_file)
        return parser

    @property
    def logger(self):
        return self._logger

    @property
    def db_host(self):
        return self._config.get('mysql=' + self._args.database, 'mysql_host', fallback='')

    @property
    def db_port(self):
        return self._config.get('mysql=' + self._args.database, 'mysql_port', fallback=None)

    @property
    def database(self):
        return self._config.get('mysql=' + self._args.database, 'mysql_base', fallback=self._args.database)

    @property
    def db_user(self):
        return self._config.get('mysql=' + self._args.database, 'mysql_user', fallback=self._args.username)

    @property
    def db_pass(self):
        return self._config.get('mysql=' + self._args.database, 'mysql_pass', fallback=self._args.password)

    @property
    def db_options(self):
        return self._config.get('mysql=' + self._args.database, 'mysql_options', fallback='')

    @property
    def save_filename(self):
        filename = self._config.get('backup', 'save_tpl', fallback='{mysql_base}.{ext}')
        return filename.format(pref=self.__pref_format(), mysql_base=self.database, ext='{ext}')

    @property
    def save_filename_mask(self):
        filename = self._config.get('backup', 'save_tpl', fallback='{mysql_base}.{ext}')
        return filename.format(pref='*', mysql_base=self.database, ext='*')

    @property
    def save_filepath(self):
        path = self._config.get('backup', 'save_dir', fallback=self._args.output)
        if path.find('./') == 0:
            dir22 = path.replace("./", "")
            path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), *dir22.split('/'))
        if not os.path.exists(path):
            os.makedirs(path)
            # OSError
        return path.format(mysql_base=self.database)

    @property
    def max_copies_count(self):
        return int(self._config.get('backup', 'max_copies_count', fallback=1))

    @property
    def is_gzip(self):
        return self._config.get('backup', 'save_gzip', fallback='True') == 'True' or self._args.gzip

    @property
    def is_encrypt(self):
        return bool(self._config.get('backup', 'encrypt_pass', fallback=self._args.encrypt))

    @property
    def compress_level(self):
        return self._config.get('backup', 'compress_level', fallback=self._args.compress_level)

    @property
    def encrypt_pass(self):
        return self._config.get('backup', 'encrypt_pass', fallback=self._args.encrypt_pass)

    # WebDAV
    @property
    def use_webdav(self):
        return True if self._args.webdav else False

    @property
    def webdav_host(self):
        if self.use_webdav:
            return self._config.get('webdav=' + self._args.webdav, 'webdav_host', fallback='')

    @property
    def webdav_user(self):
        if self.use_webdav:
            return self._config.get('webdav=' + self._args.webdav, 'webdav_user', fallback='')

    @property
    def webdav_pass(self):
        if self.use_webdav:
            return self._config.get('webdav=' + self._args.webdav, 'webdav_pass', fallback='')

    @property
    def webdav_dir(self):
        if self.use_webdav:
            return self._config.get('webdav=' + self._args.webdav, 'webdav_dir', fallback='/')

    @property
    def webdav_max_copies_count(self):
        if self.use_webdav:
            return int(self._config.get('webdav=' + self._args.webdav, 'max_copies_count', fallback=1))

    # Send email
    @property
    def use_sendmail(self):
        return True if self._args.sendmail else False

    @property
    def email_transport(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'transport', fallback='smtp')

    @property
    def email_from(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'send_from', fallback=None)

    @property
    def email_to(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'send_to', fallback=None)

    @property
    def email_cc(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'send_cc', fallback=None)

    @property
    def email_bcc(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'send_bcc', fallback=None)

    @property
    def email_subject(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'send_subject', fallback='')

    # SMTP settings
    @property
    def smtp_api_domain(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'api_domen', fallback=None)

    @property
    def smtp_api_token(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'api_token', fallback=None)

    @property
    def smtp_host(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'smtp_host', fallback=None)

    @property
    def smtp_port(self):
        if self.use_sendmail:
            return int(self._config.get('sendmail', 'smtp_port', fallback=0))

    @property
    def smtp_ssl(self):
        if self.use_sendmail:
            return bool(self._config.get('sendmail', 'smtp_ssl', fallback='False') == 'True')

    @property
    def smtp_tls(self):
        if self.use_sendmail:
            return bool(self._config.get('sendmail', 'smtp_tls', fallback='False') == 'True')

    @property
    def smtp_user(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'smtp_user', fallback='')

    @property
    def smtp_pass(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'smtp_pass', fallback='')

    # sendmail setting
    @property
    def email_limit_size_attach(self):
        if self.use_sendmail:
            return self.__format_text_size(self._config.get('sendmail', 'limit_size_source', fallback=0))

    @property
    def email_chunk_max_size(self):
        if self.use_sendmail:
            return self.__format_text_size(self._config.get('sendmail', 'chunk_max_size', fallback=0))

    def __pref_format(self):
        pref = self._config.get('backup', 'save_pref', fallback='%Y%m%d')
        if '%' in pref:
            pref = time.strftime(pref)
        return pref

    @staticmethod
    def __format_text_size(str_size):
        if isinstance(str_size, int):
            return str_size

        symbols = {'K': 2**10, 'M': 2**20}
        letter = str_size[-1].strip().upper()
        if letter in symbols:
            str_size = int(str_size[:-1]) * int(symbols[letter])

        return str_size
