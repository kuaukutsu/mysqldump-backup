import os
import requests
import shutil
import config as cfg
from utils import split
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
        self._config.logger.info('sendmail run')

        filesize = os.path.getsize(self._filepath)
        self._config.logger.info('backup size {0}'.format(filesize))

        # limit size
        if 0 < self._config.email_limit_size_attach < filesize:
            raise Exception('InvalidConfigException')

        # split
        if 0 < self._config.email_chunk_max_size < filesize:
            # work directory
            dir_split = os.path.join(os.path.dirname(self._filepath), 'split')
            if not os.path.exists(dir_split):
                os.mkdir(dir_split)

            # 7z a -vSIZE
            split(self._filepath,
                  os.path.join(dir_split, os.path.basename(self._filepath)),
                  str(self._config.email_chunk_max_size) + 'b')

            for f in os.listdir(dir_split):
                if os.path.isfile(os.path.join(dir_split, f)):
                    filepath = os.path.join(dir_split, f)
                    getattr(self, 'transport_{}'.format(self._config.email_transport))(filepath)
                    os.remove(filepath)

            # clear directory
            shutil.rmtree(dir_split)
        else:
            getattr(self, 'transport_{}'.format(self._config.email_transport))(self._filepath)

    def transport_smtp(self, filepath):
        self._config.logger.info('use transport smtp')

        msg = MIMEMultipart()
        msg['From'] = self._config.email_from
        msg['To'] = self._config.email_from
        msg['Subject'] = self._config.email_subject.format(filename=os.path.basename(filepath))
        msg.attach(MIMEText("mysqldump backup"))

        # attach
        with open(filepath) as fil:
            part = MIMEApplication(fil.read(), Name=fil.name)
            part['Content-Disposition'] = 'attachment; filename="%s"' % fil.name
            msg.attach(part)

        if self._config.smtp_ssl:
            from smtplib import SMTP_SSL
            smtp = SMTP_SSL(self._config.smtp_host, self._config.smtp_port)
        else:
            from smtplib import SMTP
            smtp = SMTP(self._config.smtp_host, self._config.smtp_port)

        smtp.set_debuglevel(False)
        if self._config.smtp_tls:
            # identify ourselves to smtp gmail client
            smtp.ehlo()
            # secure our email with tls encryption
            smtp.starttls()
            # re-identify ourselves as an encrypted connection
            smtp.ehlo()

        try:
            smtp.login(self._config.smtp_user, self._config.smtp_pass)
            smtp.sendmail(self._config.email_from, self._config.email_to, msg.as_string())
        finally:
            smtp.quit()

    def transport_api(self, filepath):
        self._config.logger.info('use transport api')

        data = {"from": self._config.email_from,
                "to": self._config.email_to,
                "subject": self._config.email_subject.format(filename=os.path.basename(filepath)),
                "text": "mysqldump backup",
                "o:tag": ["backup", self._config.database]}

        if self._config.email_cc:
            data['cc'] = self._config.email_cc

        if self._config.email_bcc:
            data['bcc'] = self._config.email_bcc

        return requests.post(
            "https://api.mailgun.net/v3/{domain_name}/messages".format(domain_name=self._config.smtp_api_domain),
            auth=("api", self._config.smtp_api_token),
            files={"attachment": open(filepath)},
            data=data)
