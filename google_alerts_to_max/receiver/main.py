from .parser import NotificationParser
from .client import ImapClient
from .models import Mention
import logging

GA_NOTIFICATIONS_ADDRESS = "googlealerts-noreply@google.com"


class Receiver:
    """
    Получатель. Обрабатывает письма уведломении Google Alerts и получает упоминания из них
    """

    def __init__(self, username: str, password: str):
        self.__logger = logging.getLogger(__name__)
        self.client = ImapClient(username, password)
        self.__logger.debug("Получатель инициализирован")

    def receive_mentions(self) -> list[Mention]:
        """
        Получить текущие упоминания из писем уведломении Google Alerts

        :return: Список последних упоминаний
        """
        self.__logger.info("Получение упоминаний из Google Alerts...")

        try:
            self.__logger.debug("Подключение к серверу IMAP...")
            self.client.connect() # подключаемся к серверу IMAP
            self.__logger.debug("Получение писем...")
            emails = self.client.fetch_mail(GA_NOTIFICATIONS_ADDRESS)
            self.__logger.debug("Получено %d писем", len(emails))
        finally:
            self.client.disconnect() # отключаемся от сервера IMAP
            self.__logger.debug("Отключение от сервера IMAP")

        # парсим упоминания из уведомлений
        self.__logger.debug("Парсинг упоминаний из писем...")
        mentions = [
            mention
            for email in emails
            for mention in NotificationParser.get_mentions(email)
            if mention
        ]
        self.__logger.info("Найдено %d упоминаний", len(mentions))

        # возвращаем только уникальные упоминания
        unique_mentions = list(set(mentions))
        self.__logger.debug("После удаления дубликатов осталось %d упоминаний", len(unique_mentions))
        return unique_mentions
