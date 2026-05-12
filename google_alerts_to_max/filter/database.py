import sqlite3

# region SQL-запросы
CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS `sent_mentions` (
    `hash` TEXT PRIMARY KEY NOT NULL,
    `added_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_HASH_QUERY = """
INSERT INTO
`sent_mentions` (`hash`)
VALUES (?)
"""

MULTIPLE_HASHES_QUERY = """
SELECT `sent_mentions`.`hash`
FROM `sent_mentions`
WHERE `sent_mentions`.`hash` IN ({})
"""

CLEAN_HASHES_QUERY = """
DELETE FROM `sent_mentions`
WHERE `sent_mentions`.`added_at` < datetime('now', '-7 days')
"""
# endregion


class Database:
    """
    База данных для хранения упоминаний
    """

    def __init__(self, path: str) -> None:
        self.__conn = sqlite3.connect(path, check_same_thread=False)

        # конфигурирование БД перед работой
        self.__enable_wal()
        self.__create_tables()

    # region Публичные методы\
    def add_sent_mentions(self, hashes: list[str]) -> None:
        """
        Добавить отправленные упоминания в БД

        :param hashes: Список уникальных хешей упоминаний
        """

        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.executemany(CREATE_HASH_QUERY, [(hash,) for hash in hashes])
            self.__conn.commit()

    def is_sent_mentions_exist(self, hashes: list[str]) -> list[bool]:
        """
        Проверить, если записи отправленных упоминаний существуют в БД

        :param hashes: Список уникальных хешей упоминаний
        :return: Список булевых значений по каждому упоминанию
        """

        with self.__conn:
            cursor = self.__conn.cursor()

            # динамически создаем запрос на основе списка хешей
            placeholders = ", ".join(["?"] * len(hashes))
            cursor.execute(MULTIPLE_HASHES_QUERY.format(placeholders), hashes)

            # получаем ответ и ищем существущие хэшы
            found_hashes = [row[0] for row in cursor.fetchall()]
            return [hash in found_hashes for hash in hashes]

    def clean_sent_mentions(self) -> None:
        """
        Очистить БД от старых записей отправленных упоминаний
        """

        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(CLEAN_HASHES_QUERY)
            self.__conn.commit()

    # endregion

    # region Приватные методы
    def __enable_wal(self) -> None:
        """
        Включить WAL режим. Необходимо для улучшения производительности
        """
        with self.__conn:
            self.__conn.execute("PRAGMA journal_mode = WAL")

    def __create_tables(self) -> None:
        """
        Организовать таблицы в подключенной БД
        """
        with self.__conn:
            self.__conn.execute(CREATE_TABLE_QUERY)

    # endregion
