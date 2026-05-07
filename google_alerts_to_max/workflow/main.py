from google_alerts_to_max.receiver import Receiver
from google_alerts_to_max.models import Mention
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
        self.__receiver = Receiver(*credentials)
        self.__filter = Filter(db_path)
        self.__sender = Sender(token, user_id, chat_id)
        self.__executor = AttemptExecutor()

    def run(self) -> None:
        """
        Запустить рабочий процесс
        """

        try:
            mentions_result = self.__executor.try_execute(
                lambda: self.__get_non_sent_mentions(),
                timeout_secs=30,
                try_wait_secs=30,
                success_condition=lambda x: len(x) > 0
            )
        except ExecutionFailedException as e:
            last_exception = e.errors[-1].exception

            if isinstance(last_exception, SuccessConditionFailedException):
                raise NoNewMentionsException(
                    "Новых упомнаний не найдено"
                ) from last_exception

            raise e

        mentions = mentions_result.result

        try:
            self.__executor.try_execute(
                lambda: self.__sender.send_mentions(mentions),
                timeout_secs=15,
                try_wait_secs=15
            )
        except ExecutionFailedException as e:
            last_exception = e.errors[-1].exception

            if isinstance(last_exception, MaxApiException):
                raise CannotSendMentionsException(
                    "Не могу отправить сообщение в Max"
                ) from last_exception

            raise e

        try:
            self.__update_filter(mentions)
        except Exception as e:
            raise CannotUpdateFilterException("Не могу обновить фильтр") from e

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
