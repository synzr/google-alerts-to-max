from dataclasses import dataclass


@dataclass
class Email:
    """
    Данные письма
    """

    id: str
    headers: dict
    body: str
