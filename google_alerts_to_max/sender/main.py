from google_alerts_to_max.receiver import Mention
from .formatter import MessageFormatter
from .client import MaxClient
from .models import BotInfo
import logging


class Sender:
    """
    Отправитель. Формирует упоминания в сообщение и отправляет его через бота в Max
    """

    def __init__(self, token: str, user_id: int | None, chat_id: int | None):
        self.__logger = logging.getLogger(__name__)
        self.__client = MaxClient(token)
        self.__formatter = MessageFormatter()

        # параметры для отправки сообщения
        self.__user_id = user_id
        self.__chat_id = chat_id
        self.__logger.debug("Отправитель инициализирован")

    def get_bot_info(self) -> BotInfo:
        """
        Получить информацию о боте в Max
        :return: Информация о боте
        """
        return self.__client.get_bot_info()

    def send_mentions(self, mentions: list[Mention]) -> None:
        """
        Отправить упоминания форматированным сообщением в Max
        :param mentions: Список упоминаний
        """
        self.__logger.info("Отправка %d упоминаний в Max...", len(mentions))
        self.__logger.debug("Форматирование сообщения...")
        message = self.__formatter.format_message(mentions)
        self.__logger.debug("Сообщение отформатировано, отправка...")
        self.__client.send_message(self.__user_id, self.__chat_id, message)
        self.__logger.info("Упоминания успешно отправлены")
