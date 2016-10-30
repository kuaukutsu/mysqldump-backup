# !/usr/bin/env python
import os
import time
from lib import config, mysql, webdav, sendmail

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
        mysqldump = mysql.Mysqldump(cfg)
        filepath = mysqldump.run()

        # exec webdav (parallel)
        if cfg.use_webdav:
            webdav.WebDAV(cfg).run()

        # exec sendmail (parallel)
        if cfg.use_sendmail:
            send = sendmail.Sendmail(cfg, filepath).run()
            print send

    except SystemExit:
        print_log('error found, process terminated')
    except Exception as e:
        print_log(e.message)


if __name__ == '__main__':
    main()
