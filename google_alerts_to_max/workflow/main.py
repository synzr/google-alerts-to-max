from google_alerts_to_max.receiver import Mention, Receiver
from google_alerts_to_max.filter import Filter
from google_alerts_to_max.sender import (
    MaxApiException,
    Sender
)
from .executor import AttemptExecutor
from .errors import (
    SuccessConditionFailedException,
    CannotSendMentionsException,
    CannotUpdateFilterException,
    ExecutionFailedException,
    NoNewMentionsException
)
import logging


class Workflow:
    """
    Рабочий процесс. Получает оповещения от Google Alerts и отправляет
    уникальные упомниания в Max
    """

    def __init__(
        self,
        credentials: tuple[str, str],
        token: str,
        db_path: str,
        user_id: int = None,
        chat_id: int = None
    ) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__receiver = Receiver(*credentials)
        self.__filter = Filter(db_path)
        self.__sender = Sender(token, user_id, chat_id)
        self.__executor = AttemptExecutor()
        self.__logger.debug("Рабочий процесс инициализирован")

    def run(self) -> None:
        """
        Запустить рабочий процесс
        """
        self.__logger.info("Запуск рабочего процесса...")

        try:
            mentions = self.__executor.try_execute(
                lambda: self.__get_non_sent_mentions(),
                timeout_secs=30,
                try_wait_secs=30,
                success_condition=lambda x: len(x) > 0
            )
            self.__logger.info("Получено %d новых упоминаний", len(mentions.result))
        except ExecutionFailedException as e:
            last_error = e.errors[-1]

            if isinstance(last_error.exception, SuccessConditionFailedException):
                raise NoNewMentionsException(
                    "Новых упомнаний не найдено",
                    error=last_error
                ) from last_error

            raise e

        try:
            self.__executor.try_execute(
                lambda: self.__sender.send_mentions(mentions.result),
                timeout_secs=15,
                try_wait_secs=15
            )
            self.__logger.info("Упоминания успешно отправлены в Max")
        except ExecutionFailedException as e:
            last_error = e.errors[-1]

            if isinstance(last_error.exception, MaxApiException):
                raise CannotSendMentionsException(
                    "Не могу отправить сообщение в Max",
                    error=last_error
                ) from last_error.exception

            raise e

        try:
            self.__executor.try_execute(
                lambda: self.__update_filter(mentions.result),
                timeout_secs=5,
                try_wait_secs=5,
            )
            self.__logger.info("Фильтр обновлен")
        except ExecutionFailedException as e:
            raise CannotUpdateFilterException(
                "Не могу обновить фильтр",
                error=e.errors[-1].exception
            ) from e.errors[-1].exception

    #region Приватные методы
    def __get_non_sent_mentions(self) -> list[Mention]:
        """
        Получить неотправленные упомниания из оповещении от Google Alerts
        :returns: Неотправленные упомниания
        """

        mentions = self.__receiver.receive_mentions()
        return self.__filter.get_non_sent_mentions(mentions)

    def __update_filter(self, mentions: list[Mention]) -> None:
        """
        Обновить фильтр. Добавить отправленные упомниания и удалить старые
        :param mentions: Отправленные упомниания
        """

        self.__filter.add_sent_mentions(mentions)
        self.__filter.clean_sent_mentions()
    #endregion
