class ImapAuthenticationException(Exception):
    """
    Исключение аутентификации при подключении к серверу IMAP
    """


class ImapNoConnectionException(Exception):
    """
    Исключение подключения к серверу IMAP
    """


class ImapNoMailboxException(Exception):
    """
    Исключение отсутствия папки в сервере IMAP
    """


class ImapServerException(Exception):
    """
    Исключение сервера IMAP
    """


class NoHtmlFoundException(Exception):
    """
    Исключение отсутствия HTML в письме
    """
