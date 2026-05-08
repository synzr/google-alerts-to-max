from bs4 import BeautifulSoup, NavigableString
from .models import Mention, Email
from yarl import URL
import re

SOURCE_LINK_STYLE = "text-decoration:none;color:#737373"
TITLE_LEFT_PAD_STYLE = "padding-left:32px"
SUBTITLE_LEFT_PAD_STYLE = "padding-left:18px"
MENTION_CONTAINER_STYLE = re.compile(r"padding:\s*18px.*vertical-align:\s*top")


class NotificationParser:
    """
    Парсер писем-уведомлений от Google Alerts
    """

    @staticmethod
    def get_mentions(email: Email) -> list[Mention]:
        """
        Получает упоминания из письма-уведомления

        :param email: Письмо-уведомление
        :return: Список упоминаний
        """
        soup = BeautifulSoup(email.body, "lxml")
        parts = NotificationParser.__parse_parts(soup)

        mentions = []
        title = None
        subtitle = None

        for part in parts:
            left_pad = part.find("td")
            if not left_pad or "style" not in left_pad.attrs:
                continue

            style = left_pad["style"]
            if style == TITLE_LEFT_PAD_STYLE:  # заголовок темы
                title = part.find("span").get_text(strip=True)
                continue
            if style == SUBTITLE_LEFT_PAD_STYLE:  # подзаголовок (тип источника); упоминания
                subtitle_container = part.find(
                    "td", {"style": "padding:16px 0px 12px 0px;border-bottom:1px solid #e4e4e4"},
                )

                if subtitle_container:
                    subtitle = subtitle_container.find("span").get_text(strip=True)
                    continue

                mention_data = NotificationParser.__extract_mention_data(part, title, subtitle)
                if mention_data:
                    mentions.append(mention_data)

        return mentions

    #region Приватные статические методы
    @staticmethod
    def __parse_parts(soup: BeautifulSoup) -> list:
        """
        Извлекает части письма из таблицы

        :param soup: BeautifulSoup объект письма
        :return: Список частей (тегов)
        """

        container = soup.find("table")
        if not container:
            return []

        tbody = container.find("tbody")
        if not tbody:
            return []

        return [
            part
            for part in tbody.contents[1:]  # пропускаем логотип Google Alerts
            if not isinstance(part, NavigableString)  # убираем пустые строки
        ]

    @staticmethod
    def __extract_mention_data(part, title: str, subtitle: str) -> Mention | None:
        """
        Извлекает данные упоминания из части

        :param part: Тег части
        :param title: Текущая тема
        :param subtitle: Текущий тип источника
        :return: Объект Mention или None если не удалось извлечь
        """

        # ищем контейнер упоминания по стилю
        mention_container = part.find("td", {"style": MENTION_CONTAINER_STYLE})
        if not mention_container:
            return None

        # получаем ссылку на упоминание
        mention_link = mention_container.find("a", {"target": "_blank"})
        if not mention_link:
            return None

        mention_url = NotificationParser.__clean_url(
            mention_link.get("href", "")
        )

        # получаем заголовок упоминания
        title_span = mention_link.find("span")
        mention_title = title_span.get_text(strip=True) if title_span else ""

        # получаем источник упоминания
        source_link = mention_container.find("a", {"style": SOURCE_LINK_STYLE})
        if source_link:
            source_span = source_link.find("span")
            mention_source = source_span.get_text(strip=True) if source_span else ""
        else:
            mention_source = ""

        return Mention(
            theme=title or "",
            source_type=subtitle or "",
            title=mention_title,
            source=mention_source,
            url=mention_url
        )

    @staticmethod
    def __clean_url(url: str) -> str:
        """
        Очистить URL от редиректора Google

        :param url: URL
        :return: Очищенный URL
        """

        parsed_url = URL(url)

        if "google" not in parsed_url.host:
            return url

        return parsed_url.query.get("url", url)
    #endregion
