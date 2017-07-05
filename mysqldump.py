# !/usr/bin/env python
import os
import sys
from lib.config import Config
from lib.mysql import Mysqldump
from lib.storage import Storage
from lib.sendmail import Sendmail

CONFIG_FILE = os.path.abspath(os.path.dirname(__file__)) + '/mysqldump.cfg'


# entry
def main():
    # build config
    cfg = Config(CONFIG_FILE)
    logger = cfg.logger

    try:
        # exec mysqldump
        filepath = Mysqldump(cfg).run()

        # exec sendmail (parallel)
        if cfg.use_sendmail:
            Sendmail(cfg, filepath).run()

        # exec webdav (parallel)
        if cfg.use_storage:
            Storage(cfg, filepath).run()

    except SystemExit:
        logger.critical('error found, process terminated')
    except Exception as e:
        logger.error(e)
    finally:
        sys.exit()


if __name__ == '__main__':
    main()
