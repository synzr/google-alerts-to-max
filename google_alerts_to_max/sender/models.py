from dataclasses import dataclass
from typing import Literal, Optional
from enum import StrEnum


@dataclass
class User:
    """
    Информация о пользователе
    """

    user_id: int
    first_name: str
    last_name: str | None
    username: str | None
    is_bot: bool
    last_activity_time: int

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            user_id=data["user_id"],
            first_name=data["first_name"],
            last_name=data.get("last_name"),
            username=data.get("username"),
            is_bot=data["is_bot"],
            last_activity_time=data["last_activity_time"],
        )


@dataclass
class BotInfo(User):
    """
    Информацию о боте
    """

    description: str | None
    avatar_url: str | None
    full_avatar_url: str | None
    commands: list["BotCommand"] | None

    @staticmethod
    def from_dict(data: dict) -> "BotInfo":
        return BotInfo(
            user_id=data["user_id"],
            first_name=data["first_name"],
            last_name=data.get("last_name"),
            username=data.get("username"),
            is_bot=data["is_bot"],
            last_activity_time=data["last_activity_time"],
            description=data.get("description"),
            avatar_url=data.get("avatar_url"),
            full_avatar_url=data.get("full_avatar_url"),
            commands=[
                BotCommand.from_dict(command)
                for command in data.get("commands", [])
            ],
        )


@dataclass
class BotCommand:
    """
    Описание команды бота
    """

    name: str
    description: str

    @staticmethod
    def from_dict(data: dict) -> "BotCommand":
        return BotCommand(
            name=data["name"],
            description=data["description"],
        )


@dataclass
class NewMessage:
    """
    Новое сообщение
    """

    text: str | None
    attachments: list["AttachmentRequest"] | None
    link: Optional["NewMessageLink"]
    notify: bool = True
    format: Optional["NewMessageFormat"] = None

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "attachments": [
                attachment.to_dict()
                for attachment in self.attachments
            ] if self.attachments else None,
            "link": self.link.to_dict() if self.link else None,
            "notify": self.notify,
            "format": self.format,
        }


@dataclass
class AttachmentRequest:
    """
    Запрос на отправку вложения
    """

    type: str
    payload: dict

    def to_dict(self) -> dict:
        return {"type": self.type, "payload": self.payload}


@dataclass
class NewMessageLink:
    """
    Ссылка внутри Max
    """

    type: "MessageLinkType"
    mid: str

    def to_dict(self) -> dict:
        return {"type": self.type, "mid": self.mid}


class NewMessageFormat(StrEnum):
    """
    Формат нового сообщения
    """

    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class Message:
    """
    Сообщение в Max
    """

    recipient: Optional["Recipient"]
    timestamp: int
    sender: User | None = None
    link: Optional["LinkedMessage"] = None
    body: Optional["MessageBody"] = None
    stat: Optional["MessageStat"] = None
    url: str | None = None

    @staticmethod
    def from_dict(data: dict) -> "Message":
        return Message(
            recipient=Recipient.from_dict(data["recipient"]),
            timestamp=data["timestamp"],
            sender=(
                User.from_dict(data["sender"])
                if data.get("sender")
                else None
            ),
            link=(
                LinkedMessage.from_dict(data["link"]) if data.get("link")
                else None
            ),
            body=(
                MessageBody.from_dict(data["body"]) if data.get("body")
                else None
            ),
            stat=(
                MessageStat.from_dict(data["stat"]) if data.get("stat")
                else None
            ),
            url=data.get("url"),
        )


@dataclass
class Recipient:
    """
    Получатель сообщения
    """

    chat_id: int
    chat_type: Literal["chat"] = "chat"  # зачем???
    user_id: int | None = None

    @staticmethod
    def from_dict(data: dict) -> "Recipient":
        return Recipient(
            chat_id=data["chat_id"],
            user_id=data.get("user_id"),
        )


@dataclass
class LinkedMessage:
    """
    Ссылка на сообщение в Max
    """

    type: "MessageLinkType"
    chat_id: int | None
    message: "MessageBody"
    sender: Optional["User"] = None

    @staticmethod
    def from_dict(data: dict) -> "LinkedMessage":
        return LinkedMessage(
            type=data["type"],
            sender=(
                User.from_dict(data["sender"]) if data.get("sender")
                else None
            ),
            message=MessageBody.from_dict(data["message"]),
            chat_id=data.get("chat_id"),
        )


@dataclass
class MessageBody:
    """
    Тело сообщения в Max
    """

    mid: str
    seq: int
    text: str | None
    attachments: list["Attachment"] | None = None
    markup: list["MarkupElement"] | None = None

    @staticmethod
    def from_dict(data: dict) -> "MessageBody":
        return MessageBody(
            mid=data["mid"],
            seq=data["seq"],
            text=data.get("text"),
            attachments=(
                [Attachment.from_dict(a) for a in data["attachments"]]
                if data.get("attachments") else None
            ),
            markup=(
                [MarkupElement.from_dict(m) for m in data["markup"]]
                if data.get("markup") else None
            ),
        )


@dataclass
class Attachment:
    """
    Вложения внутри сообщения в Max
    """

    type: str
    payload: dict

    def to_dict(self) -> dict:
        return {"type": self.type, "payload": self.payload}


@dataclass
class MarkupElement:
    """
    Разметка текста сообщения в Max
    """

    type: str
    from_: int
    length: int
    extra: dict

    @staticmethod
    def from_dict(data: dict) -> "MarkupElement":
        return MarkupElement(
            type=data["type"],
            from_=data["from"],
            length=data["length"],
            extra={
                key: value
                for key, value in data.items()
                if key not in ["type", "from", "length"]
            },
        )


@dataclass
class MessageStat:
    """
    Статистика сообщения в Max
    """

    views: int

    @staticmethod
    def from_dict(data: dict) -> "MessageStat":
        return MessageStat(views=data["views"])


class MessageLinkType(StrEnum):
    """
    Тип ссылки на сообщение в Max
    """

    FORWARD = "forward"
    REPLY = "reply"
