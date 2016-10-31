# !/usr/bin/env python
import os
import time
from lib import config, mysql, storage, sendmail

CONFIG_FILE = os.path.abspath(os.path.dirname(__file__)) + '/mysqldump.cfg'


# Defining method to unify format of output info
def print_log(log_text):
    log_prefix = '[{0}]'.format(time.strftime('%Y-%m-%d %H:%M:%S'))
    print('{0} {1}'.format(log_prefix, log_text))


# entry
def main():
    try:
        # build config
        cfg = config.Config(CONFIG_FILE)

        # exec mysqldump
        filepath = mysql.Mysqldump(cfg).run()

        # exec webdav (parallel)
        if cfg.use_webdav:
            storage.Storage(cfg, filepath).run()

        # exec sendmail (parallel)
        if cfg.use_sendmail:
            sendmail.Sendmail(cfg, filepath).run()

    except SystemExit:
        print_log('error found, process terminated')
    except Exception as e:
        print_log(e.message)


if __name__ == '__main__':
    main()
