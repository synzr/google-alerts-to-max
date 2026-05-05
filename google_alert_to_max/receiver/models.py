from dataclasses import dataclass


@dataclass
class Email:
    """
    Данные письма
    """

    id: str
    headers: dict
    body: str


@dataclass(frozen=True)
class Mention:
    """
    Упоминание из Google Alerts
    """

    theme: str
    source_type: str
    title: str
    source: str
    url: str
