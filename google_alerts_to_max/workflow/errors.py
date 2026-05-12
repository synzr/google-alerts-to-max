from .models import ErrorAttempt


class SuccessConditionFailedException(Exception):
    """
    Исключение проваленного условия успешного выполнения
    """

    def __init__(self, message: str, result: any) -> None:
        super().__init__(message)
        self.result = result


class ExecutionFailedException(Exception):
    """
    Исключение проваленного исполнения вызываемого
    """

    def __init__(
        self,
        message: str,
        attempts: int,
        time_taken_secs: int,
        errors: list[ErrorAttempt],
    ) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.time_taken_secs = time_taken_secs
        self.errors = errors


class NoNewMentionsException(Exception):
    """
    Исключение отсутствия новых упоминании
    """

    def __init__(self, message: str, error: ErrorAttempt) -> None:
        super().__init__(message)
        self.error = error


class CannotSendMentionsException(Exception):
    """
    Исключение невозможности отправка упоминании
    """

    def __init__(self, message: str, error: ErrorAttempt) -> None:
        super().__init__(message)
        self.error = error


class CannotUpdateFilterException(Exception):
    """
    Исключение невозможности обновить фильтр
    """

    def __init__(self, message: str, error: ErrorAttempt) -> None:
        super().__init__(message)
        self.error = error
