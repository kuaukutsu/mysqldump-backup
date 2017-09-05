# !/usr/bin/env python
import sys
from lib.app import App
from lib.mysql import Mysqldump
from lib.storage import Storage
from lib.sendmail import Sendmail


# entry
def main():

    app = App()

    try:
        # exec mysqldump
        filepath = Mysqldump(app).run()

        # exec sendmail (parallel)
        if app.config.use_sendmail:
            Sendmail(app, filepath).run()

        # exec webdav (parallel)
        if app.config.use_storage:
            Storage(app, filepath).run()

    except SystemExit:
        app.logger.critical('error found, process terminated')
    except Exception as e:
        app.logger.error(e)
    finally:
        sys.exit()


if __name__ == '__main__':
    main()
