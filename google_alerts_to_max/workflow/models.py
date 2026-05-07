from dataclasses import dataclass


@dataclass
class SuccessAttemptResult:
    """
    Успешный результат выполнения
    """

    attempts_used: int
    time_taken_secs: int
    errors: list["ErrorAttempt"]
    result: any


@dataclass
class ErrorAttempt:
    """
    Полная информация об ошибке во исполнения
    """

    exception: Exception
    traceback: str
    attempt: int
    timestamp: int
