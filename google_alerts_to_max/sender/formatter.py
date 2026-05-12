from jinja2 import Environment, PackageLoader, select_autoescape
from google_alerts_to_max.receiver import Mention
from .models import NewMessage, NewMessageFormat


class MessageFormatter:
    """
    Форматирует из упоминании готовые сообщения для отправки в Max
    """

    def __init__(self):
        self.__env = Environment(
            loader=PackageLoader("google_alerts_to_max"), autoescape=select_autoescape()
        )

    def format_message(self, mentions: list[Mention]) -> NewMessage:
        """
        Форматирует упоминания в сообщение для отправки в Max
        """

        text = self.__env.get_template("mentions.html").render(mentions=mentions)

        return NewMessage(
            text,
            format=NewMessageFormat.HTML,
            attachments=None,
            link=None,
        )
