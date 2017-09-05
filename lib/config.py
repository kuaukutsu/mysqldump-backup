#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import argparse
from configparser import RawConfigParser as ConfigParser


class Config(object):
    def __init__(self, configure_file):
        self._args = self.__parse_args(configure_file)
        self._config = self.__parse_config()

    def __parse_args(self, configure_file):
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
        parser.add_argument("--storage",
                            dest="storage",
                            type=str,
                            help="copy mysqldump to Nameserver")
        parser.add_argument("--sendmail",
                            dest="sendmail",
                            type=str,
                            help="send email")
        parser.add_argument("--options",
                            dest="options",
                            type=str,
                            help="options for mysqldump")

        args = parser.parse_args()

        # path file configure
        self._config_file = os.path.abspath(args.config) if args.config else configure_file

        if args.logfile:
            # create
            dirlog = os.path.dirname(args.logfile)
            if not os.path.exists(dirlog):
                os.makedirs(dirlog)

        if args.encrypt_pass:
            args.gzip = False
            args.encrypt = True

        return args

    def __parse_config(self):
        parser = ConfigParser()
        if not os.path.exists(self._config_file):
            raise IOError('Configuration file not found at: {0}, exit'.format(os.path.abspath(self._config_file)))
        parser.read(self._config_file)
        return parser

    @property
    def logfile(self):
        return self._args.logfile

    @property
    def db_host(self):
        return self._config.get('mysql=' + self._args.database, 'host', fallback='')

    @property
    def db_port(self):
        return self._config.get('mysql=' + self._args.database, 'port', fallback=None)

    @property
    def database(self):
        return self._config.get('mysql=' + self._args.database, 'base', fallback=self._args.database)

    @property
    def db_user(self):
        return self._config.get('mysql=' + self._args.database, 'user', fallback=self._args.username)

    @property
    def db_pass(self):
        return self._config.get('mysql=' + self._args.database, 'pass', fallback=self._args.password)

    @property
    def db_options(self):
        return self._config.get('mysql=' + self._args.database, 'options', fallback='')

    @property
    def save_filename(self):
        filename = self._config.get('backup', 'save_tpl', fallback='{base}.{ext}')
        return filename.format(pref=self.__pref_format(), base=self.database, ext='{ext}')

    @property
    def save_filename_mask(self):
        filename = self._config.get('backup', 'save_tpl', fallback='{base}.{ext}')
        return filename.format(pref='*', base=self.database, ext='*')

    @property
    def save_filepath(self):
        path = self._config.get('backup', 'save_dir', fallback=self._args.output)
        if path.find('./') == 0:
            dir22 = path.replace("./", "")
            path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), *dir22.split('/'))
        if not os.path.exists(path):
            os.makedirs(path)
            # OSError
        return path.format(base=self.database)

    @property
    def max_copies(self):
        return int(self._config.get('backup', 'max_copies', fallback=1))

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

    # storage
    @property
    def use_storage(self):
        return True if self._args.storage else False

    @property
    def storage_transport(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'transport', fallback='webdav')

    @property
    def storage_host(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'host', fallback='')

    @property
    def storage_user(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'user', fallback='')

    @property
    def storage_pass(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'pass', fallback='')

    @property
    def storage_proxy_host(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'proxy_host', fallback=None)

    @property
    def storage_proxy_user(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'proxy_user', fallback=None)

    @property
    def storage_proxy_pass(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'proxy_pass', fallback=None)

    @property
    def storage_cert_path(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'cert_path', fallback=None)

    @property
    def storage_key_path(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'key_path', fallback=None)

    @property
    def storage_token(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'token', fallback=None)

    @property
    def storage_port(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'port', fallback=None)

    @property
    def storage_dir(self):
        if self.use_storage:
            return self._config.get('storage=' + self._args.storage, 'dir', fallback='/')

    @property
    def storage_max_copies(self):
        if self.use_storage:
            return int(self._config.get('storage=' + self._args.storage, 'max_copies', fallback=1))

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
            return self._config.get('sendmail=' + self._args.sendmail, 'from', fallback=None)

    @property
    def email_to(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'to', fallback=None)

    @property
    def email_cc(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'cc', fallback=None)

    @property
    def email_bcc(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'bcc', fallback=None)

    @property
    def email_subject(self):
        if self.use_sendmail:
            return self._config.get('sendmail=' + self._args.sendmail, 'subject', fallback='')

    # SMTP settings
    @property
    def sendmail_api_domain(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'domen', fallback=None)

    @property
    def sendmail_api_token(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'token', fallback=None)

    @property
    def sendmail_host(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'host', fallback=None)

    @property
    def sendmail_port(self):
        if self.use_sendmail:
            return int(self._config.get('sendmail', 'port', fallback=0))

    @property
    def sendmail_ssl(self):
        if self.use_sendmail:
            return bool(self._config.get('sendmail', 'ssl', fallback='False') == 'True')

    @property
    def sendmail_tls(self):
        if self.use_sendmail:
            return bool(self._config.get('sendmail', 'tls', fallback='False') == 'True')

    @property
    def sendmail_user(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'user', fallback='')

    @property
    def sendmail_pass(self):
        if self.use_sendmail:
            return self._config.get('sendmail', 'pass', fallback='')

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
