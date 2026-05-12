from pathlib import Path
from decouple import config


def int_or_none(value: str | None) -> int | None:
    try:
        value = int(value)

        if not value:
            return None

        return value
    except (TypeError, ValueError):
        return None


# Токен бота в Max и идентификатор пользователя/чата
MAX_TOKEN = config("MAX_TOKEN")
MAX_USER_ID = config("MAX_USER_ID", cast=int_or_none, default=None)
MAX_CHAT_ID = config("MAX_CHAT_ID", cast=int_or_none, default=None)

if MAX_USER_ID is None and MAX_CHAT_ID is None:
    raise ValueError("MAX_USER_ID/MAX_CHAT_ID не представлен")
if MAX_USER_ID is not None and MAX_CHAT_ID is not None:
    raise ValueError("MAX_USER_ID/MAX_CHAT_ID не могут быть представлены одновременно")

# Учетные данные к аккаунту Gmail
GMAIL_CREDENTIALS_USER = config("GMAIL_CREDENTIALS_USER")
GMAIL_CREDENTIALS_PASS = config("GMAIL_CREDENTIALS_PASS")

# Путь к БД фильтра
FILTER_DB_PATH = config(
    "FILTER_DB_PATH", cast=Path, default=Path(__file__).parent.parent / "filter.db"
)

# Настройка логирования
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FILE_PATH = config(
    "LOG_FILE_PATH",
    cast=Path,
    default=Path(__file__).parent.parent / "google-alerts-to-max.log",
)
