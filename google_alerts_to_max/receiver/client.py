from email.message import Message
from .errors import (
    ImapAuthenticationException,
    ImapNoConnectionException,
    ImapNoMailboxException,
    NoHtmlFoundException,
    ImapServerException
)
from imaplib import IMAP4_SSL
from .models import Email
from email import policy
import email

IMAP_SERVER = "imap.gmail.com"


class ImapClient:
    """
    Клиент для работы с сервером IMAP Gmail
    """

    def __init__(self, username: str, password: str) -> None:
        self.credentials = (username, password)

    #region Публичные методы
    def connect(self) -> None:
        """
        Подключаться к серверу IMAP Gmail.
        """

        self.imap = IMAP4_SSL(IMAP_SERVER)

        try:
            self.imap.login(*self.credentials)
        except IMAP4_SSL.error as e:
            raise ImapAuthenticationException(
                "Ошибка аутентификации, проверите учетные данные"
            ) from e
        except IMAP4_SSL.abort as e:
            raise ImapServerException(
                f"При аутентификации на сервере произошла ошибка: {e}"
            ) from e

    def disconnect(self) -> None:
        """
        Отключаться от сервера IMAP Gmail
        """

        try:
            self.imap.close()
            self.imap.logout()
        except IMAP4_SSL.abort as e:
            raise ImapServerException(
                f"При отключении от сервера произошла ошибка: {e}"
            ) from e

        del self.imap

    def fetch_mail(self, address: str, size: int = 10) -> list[Email]:
        """
        Получить письма от отдельного адреса (address) до максимального количества (size)

        :param address: Адрес отправителя
        :param size: Максимальное количество писем (по умолчанию: 10)
        :return: Список писем с заголовками и телом
        """

        if not self.imap:
            raise ImapNoConnectionException("Отсутствует подключение к серверу")

        try:
            self.imap.select('INBOX')
        except IMAP4_SSL.error as e:
            raise ImapNoMailboxException(
                f"Не удалось получить доступ к папке INBOX: {e}"
            ) from e

        try:
            # ищем ID писем от отдельного адреса
            _, data = self.imap.search(None, f"(FROM {address})")
            message_ids = data[0].split()[:size]

            # получаем письма
            messages = []
            for email_id in message_ids:
                # загружаем сырые данные письма
                _, rfc822_data = self.imap.fetch(email_id, "(RFC822)")
                raw_message = rfc822_data[0][1]

                # парсим письмо
                messages.append(
                    self.__parse_raw_message(email_id, raw_message),
                )
            return messages
        except IMAP4_SSL.error as e:
            raise ImapServerException(
                f"При поиске писем от адреса {address} произошла ошибка: {e}"
            ) from e
    #endregion

    #region Приватные методы
    def __get_html_body(self, message: Message) -> Message:
        """
        Получить HTML-тело письма из сырых данных.

        :param message: Сырые данные письма
        :return: HTML-тело письма
        """

        # если письмо содержит несколько частей, ищем HTML-тело
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode()

        # если письмо содержит только HTML-тело, возвращаем его
        if message.get_content_type() == "text/html":
            return message.get_payload(decode=True).decode()

        raise NoHtmlFoundException("HTML-тело не найдено")

    def __parse_raw_message(self, email_id: bytes, raw_message: bytes) -> Email:
        """
        Спарсить сырые данные письма и получить заголовки и тело из него.

        :param email_id: ID письма
        :param raw_message: Сырые данные письма в формате RFC822
        :return: Распаршенное письмо
        """

        message = email.message_from_bytes(
            raw_message, policy=policy.default,
        )

        # извлекаем заголовки
        headers = dict(message.items())

        # извлекаем тело письма
        body = self.__get_html_body(message)

        return Email(id=email_id.decode(), headers=headers, body=body)
    #endregion
