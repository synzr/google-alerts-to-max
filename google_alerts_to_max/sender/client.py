from .models import NewMessage, Message, BotInfo
from .errors import MaxApiException
from requests import Session

USER_AGENT = "google-alerts-to-max/1.0 (+https://github.com/synzr/google-alerts-to-max)"
BASE_URL = "https://platform-api.max.ru"


class MaxClient:
    """
    Клиент к API мессенджера Max
    """

    def __init__(self, token: str) -> None:
        self.__session = Session()

        # устанавливаем заголовки
        self.__session.headers.update({
            "User-Agent": USER_AGENT,
            "Authorization": token,
        })

    def get_bot_info(self) -> BotInfo:
        """
        Получить информацию о боте в Max
        :return: Информация о боте
        """

        try:
            with self.__session.get(f"{BASE_URL}/me") as r:
                # проверяем статус ответа
                r.raise_for_status()

                # возвращаем информацию о боте
                return BotInfo.from_dict(r.json())
        except Exception as e:
            raise MaxApiException("Ошибка при получении информации о боте") from e

    def send_message(
        self,
        user_id: int | None,
        chat_id: int | None,
        message: NewMessage,
    ) -> Message:
        """
        Отправить сообщение пользователю/чату в Max

        :param user_id: ID пользователя
        :param chat_id: ID чата
        :param message: Новое сообщение

        :returns: Отправленное сообщение
        """

        if user_id is None and chat_id is None:
            raise ValueError("Не указан user_id или chat_id")

        params = (
            {"user_id": user_id} if user_id is not None
            else {"chat_id": chat_id}
        )

        try:
            with self.__session.post(
                f"{BASE_URL}/messages",
                params=params,
                json=message.to_dict(),
            ) as r:
                data = r.json()
                print(data)

                # проверяем статус ответа
                r.raise_for_status()

                # возвращаем информацию об отправленном сообщении
                return Message.from_dict(data["message"])
        except Exception as e:
            raise MaxApiException("Ошибка при отправке сообщения") from e
