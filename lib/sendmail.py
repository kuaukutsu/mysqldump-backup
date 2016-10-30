import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import config as cfg


class Sendmail(object):
    """
    https://docs.python.org/2/library/email-examples.html
    https://documentation.mailgun.com/user_manual.html#sending-via-api
    https://documentation.mailgun.com/user_manual.html#sending-via-smtp
    """
    def __init__(self, config, filepath):
        if not isinstance(config, cfg.Config):
            raise Exception('InvalidConfigException')
        self._config = config

        if not os.path.exists(filepath):
            raise IOError('Attach file not found at: {0}, exit'.format(os.path.abspath(filepath)))
        self._filepath = os.path.abspath(filepath)

    def run(self):
        return getattr(self, 'transport_{}'.format(self._config.email_transport))()

    def send_data(self):
        data = {"from": self._config.email_from,
                "to": self._config.email_to,
                "subject": self._config.email_subject.format(filename=os.path.basename(self._filepath)),
                "text": "Mysqldump backup"}

        if self._config.email_cc:
            data['cc'] = self._config.email_cc

        if self._config.email_bcc:
            data['bcc'] = self._config.email_bcc

        return data

    @property
    def send_files(self):
        # check size
        return [("attachment", open(self._filepath))]

    def transport_smtp(self):
        msg = MIMEMultipart()
        msg['From'] = self._config.email_from
        msg['To'] = self._config.email_from
        msg['Subject'] = self._config.email_subject
        msg.attach(MIMEText("Mysqldump backup"))

        # attach
        for f in self.send_files or []:
            name, filelink = f
            with filelink as fil:
                part = MIMEApplication(fil.read(), Name=os.path.basename(f))
                part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
                msg.attach(part)

        smtp = smtplib.SMTP(self._config.smtp_host, self._config.smtp_port)
        smtp.sendmail(self._config.email_from, self._config.email_to, msg.as_string())
        smtp.close()

    def transport_api(self):
        return requests.post(
            "https://api.mailgun.net/v3/{domain_name}/messages".format(domain_name=self._config.smtp_api_domain),
            auth=("api", self._config.smtp_api_token),
            files=self.send_files,
            data=self.send_data())
