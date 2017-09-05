import os
import requests
from app import App

MSG_BODY = "mysqldump backup"


class Mailgun(object):
    """
        https://documentation.mailgun.com/user_manual.html#sending-via-api
        https://documentation.mailgun.com/user_manual.html#sending-via-smtp
    """
    def __init__(self, app):
        if not isinstance(app, App):
            raise Exception('InvalidConfigException')

        self._config = app.config
        self._logger = app.logger

    def send(self, filepath):
        data = {
            "from": self._config.email_from,
            "to": self._config.email_to,
            "subject": self._config.email_subject.format(filename=os.path.basename(filepath)),
            "text": MSG_BODY,
            "o:tag": ["backup", self._config.database]
        }

        if self._config.email_cc:
            data['cc'] = self._config.email_cc

        if self._config.email_bcc:
            data['bcc'] = self._config.email_bcc

        response = requests.post(
            "https://api.mailgun.net/v3/{domain_name}/messages".format(domain_name=self._config.sendmail_api_domain),
            auth=("api", self._config.sendmail_api_token),
            files={"attachment": open(filepath)},
            data=data)

        self._logger.debug('mailgun response: {0}'.format(response))

        return response
