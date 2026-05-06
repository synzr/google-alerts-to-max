from .parser import NotificationParser
from .client import ImapClient

GA_NOTIFICATIONS_ADDRESS = "googlealerts-noreply@google.com"


class Receiver:
    """
    Получатель. Обрабатывает письма уведломении Google Alerts и получает упоминания из них
    """

    def __init__(self, username: str, password: str):
        self.client = ImapClient(username, password)

    def receive_mentions(self) -> list:
        """
        Получить текущие упоминания из писем уведломении Google Alerts

        :return: Список последних упоминаний
        """

        try:
            self.client.connect() # подключаемся к серверу IMAP
            emails = self.client.fetch_mail(GA_NOTIFICATIONS_ADDRESS)
        finally:
            self.client.disconnect() # отключаемся от сервера IMAP

        # парсим упоминания из уведомлений
        mentions = [
            mention
            for email in emails
            for mention in NotificationParser.get_mentions(email)
            if mention
        ]

        # возвращаем только уникальные упоминания
        return list(set(mentions))
