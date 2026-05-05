class ImapAuthenticationException(Exception):
    """
    Исключение аутентификации при подключении к серверу IMAP
    """

    pass


class ImapNoConnectionException(Exception):
    """
    Исключение подключения к серверу IMAP
    """

    pass


class ImapNoMailboxException(Exception):
    """
    Исключение отсутствия папки в сервере IMAP
    """

    pass


class ImapServerException(Exception):
    """
    Исключение сервера IMAP
    """

    pass


class NoHtmlFoundException(Exception):
    """
    Исключение отсутствия HTML в письме
    """

    pass
