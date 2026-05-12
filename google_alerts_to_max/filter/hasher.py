import hashlib
from google_alerts_to_max.receiver import Mention


class MentionHasher:
    """
    Хэшер упоминаний. Использует ссылки в упоминаниях как уникальный ключ
    """

    @staticmethod
    def hash_mention(mention: Mention) -> str:
        """
        Хэшировать упоминание

        :param mention: Упоминание
        :return: Хеш упоминания
        """
        return hashlib.sha1(mention.url.encode()).hexdigest()
