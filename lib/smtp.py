import os
from config import Config
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MSG_BODY = "mysqldump backup"


class Smtp(object):
    """
        https://docs.python.org/2/library/email-examples.html
    """
    def __init__(self, config):
        if not isinstance(config, Config):
            raise Exception('InvalidConfigException')

        self._config = config
        self._logger = config.logger

    def send(self, filepath):
        msg = MIMEMultipart()
        msg['From'] = self._config.email_from
        msg['To'] = self._config.email_from
        msg['Subject'] = self._config.email_subject.format(filename=os.path.basename(filepath))
        msg.attach(MIMEText(MSG_BODY))

        # attach
        with open(filepath) as fil:
            part = MIMEApplication(fil.read(), Name=fil.name)
            part['Content-Disposition'] = 'attachment; filename="%s"' % fil.name
            msg.attach(part)

        if self._config.sendmail_ssl:
            from smtplib import SMTP_SSL
            smtp = SMTP_SSL(self._config.sendmail_host, self._config.sendmail_port)
        else:
            from smtplib import SMTP
            smtp = SMTP(self._config.sendmail_host, self._config.sendmail_port)

        smtp.set_debuglevel(False)
        if self._config.sendmail_tls:
            # identify ourselves to smtp gmail client
            smtp.ehlo()
            # secure our email with tls encryption
            smtp.starttls()
            # re-identify ourselves as an encrypted connection
            smtp.ehlo()

        try:
            smtp.login(self._config.sendmail_user, self._config.sendmail_pass)
            smtp.sendmail(self._config.email_from, self._config.email_to, msg.as_string())
        finally:
            smtp.quit()
