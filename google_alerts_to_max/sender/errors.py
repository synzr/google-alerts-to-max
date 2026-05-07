class MaxApiException(Exception):
    """
    Исключение при работе с API Max
    """

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code
