# !/usr/bin/env python
import os
from lib import config, mysql, storage, sendmail

CONFIG_FILE = os.path.abspath(os.path.dirname(__file__)) + '/mysqldump.cfg'


# entry
def main():
    # build config
    cfg = config.Config(CONFIG_FILE)

    try:
        # exec mysqldump
        filepath = mysql.Mysqldump(cfg).run()

        # exec webdav (parallel)
        if cfg.use_webdav:
            storage.Storage(cfg, filepath).run()

        # exec sendmail (parallel)
        if cfg.use_sendmail:
            sendmail.Sendmail(cfg, filepath).run()

    except SystemExit:
        cfg.logger.critical('error found, process terminated')
    except Exception as e:
        cfg.logger.error(e.message)


if __name__ == '__main__':
    main()
