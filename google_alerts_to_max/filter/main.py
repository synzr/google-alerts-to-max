from google_alerts_to_max.receiver import Mention
from .hasher import MentionHasher
from .database import Database
import logging


class Filter:
    """
    Фильтр на неотправленные упоминания. Использует БД для хранения уже отправленных упоминаний
    """

    def __init__(self, db_path: str) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__db = Database(db_path)
        self.__logger.debug("Фильтр инициализирован с базой данных: %s", db_path)

    def get_non_sent_mentions(self, mentions: list[Mention]) -> list[Mention]:
        """
        Отфильтроват упоминания от уже отправленных

        :param mentions: Список упоминаний
        :return: Список новых упоминаний
        """
        self.__logger.debug("Фильтрация %d упоминаний на уже отправленные", len(mentions))
        mention_checks = self.__db.is_sent_mentions_exist(
            self.__hash_mentions(mentions)
        )

        non_sent_mentions = []
        for i, mention in enumerate(mentions):
            if not mention_checks[i]:  # если упоминание НЕ отправлено, добавляем его
                non_sent_mentions.append(mention)
        self.__logger.info("После фильтрации осталось %d новых упоминаний", len(non_sent_mentions))
        return non_sent_mentions

    def add_sent_mentions(self, mentions: list[Mention]) -> None:
        """
        Добавить отправленные упоминания в БД
        :param mention: Упоминание
        """
        self.__logger.debug("Добавление %d отправленных упоминаний в БД", len(mentions))
        self.__db.add_sent_mentions(
            self.__hash_mentions(mentions)
        )
        self.__logger.info("Отправленные упоминания добавлены в БД")

    def clean_sent_mentions(self) -> None:
        """
        Очистить БД фильтра от старых отправленных упоминания в БД
        """
        self.__logger.debug("Очистка старых отправленных упоминаний из БД")
        self.__db.clean_sent_mentions()
        self.__logger.info("Старые отправленные упоминания очищены из БД")

    def __hash_mentions(self, mentions: list[Mention]) -> list[str]:
        """
        Хеширование упоминаний

        :param mentions: Список упоминаний
        :return: Список хешей
        """
        return [MentionHasher.hash_mention(mention) for mention in mentions]
