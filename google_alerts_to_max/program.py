from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.interval import IntervalTrigger
from google_alerts_to_max.workflow import (
    CannotUpdateFilterException,
    CannotSendMentionsException,
    ExecutionFailedException,
    NoNewMentionsException,
    Workflow
)
import logging.config
from .config import (
    MAX_TOKEN,
    MAX_USER_ID,
    MAX_CHAT_ID,
    GMAIL_CREDENTIALS_USER,
    GMAIL_CREDENTIALS_PASS,
    FILTER_DB_PATH,
    LOG_LEVEL,
    LOG_FILE_PATH
)
import traceback
import logging
import time
import math


class Program:
    """
    Программа. Настраивает планировщик и время от времени
    запускает рабочий процесс
    """

    def __init__(self):
        # настройка логгера
        self.__setup_logging()
        self.__logger = logging.getLogger(__name__)

        # создание рабочего процесса
        gmail_credentials = (
            GMAIL_CREDENTIALS_USER,
            GMAIL_CREDENTIALS_PASS,
        )
        self.__workflow = Workflow(
            credentials=gmail_credentials,
            token=MAX_TOKEN,
            db_path=FILTER_DB_PATH,
            user_id=MAX_USER_ID,
            chat_id=MAX_CHAT_ID,
        )
        self.__logger.debug("Рабочий процесс создан")

        # создание планировщика
        self.__scheduler = BlockingScheduler(
            jobstores={"default": MemoryJobStore()},
            executors={"default": ThreadPoolExecutor()},
            job_defaults={
                "coalesce": False,
                "max_instances": 1
            }
        )
        self.__logger.debug("Планировщик создан")

    def main(self) -> None:
        """
        Основная функция программы
        """

        # настраиваем планировщик и запускаем его
        self.__scheduler.add_job(
            lambda: self.__workflow_run(),
            IntervalTrigger(
                hours=4,
                jitter=120, # 0с...2м задержки
            ),
        )

        try:
            self.__logger.info("Планировщик запущен...")
            self.__scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.__logger.info("Остановляем планировщик...")
            self.__scheduler.shutdown()
        except Exception as e:
            self.__logger.debug(f"Ошибка: {e}")

    def __workflow_run(self) -> None:
        """
        Обертка над workflow.run() для логгеривания ошибок.
        """

        try:
            self.__workflow.run()
            self.__logger.info("Рабочий процесс успешно выполнен!")
        except (
            NoNewMentionsException,
            CannotSendMentionsException,
            CannotUpdateFilterException
        ) as e:
            self.__logger.info("%s:", e.args[0])
            self.__logger.error("\tОшибка - %s:", str(e.error.exception))
            self.__logger.error("\tВремя ошибки в Unix: %d", e.error.timestamp)
            self.__logger.error("\tTraceback:\n%s", e.error.traceback)
        except ExecutionFailedException as e:
            self.__logger.error("Неизвестная ошибка выполнения:")
            self.__logger.error("\tКоличество попыток: %d", e.attempts)
            self.__logger.error("\tПотраченное время: %d", e.time_taken_secs)
            self.__logger.error("\tКоличество ошибок: %d", len(e.errors))

            for i, error in enumerate(e.errors):
                self.__logger.error("\t\tОшибка №%d - %s:", i + 1, str(error.exception))
                self.__logger.error("\t\tНомер попытки: %d", error.attempt)
                self.__logger.error("\t\tВремя ошибки в Unix: %d", error.timestamp)
                self.__logger.error("\t\tTraceback:\n%s", error.traceback)
        except Exception as e:
            self.__logger.error("Неизвестная ошибка:")
            self.__logger.error("\tВремя ошибка в Unix: %3.14f", math.floor(time.time()))
            self.__logger.error("\tTraceback:\n%s", traceback.format_exc())

    def __setup_logging(self) -> None:
        """
        Глобально настроить логгер
        """

        logging.config.dictConfig({
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default"
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": str(LOG_FILE_PATH),
                    "formatter": "default",
                    "encoding": "utf-8"
                }
            },
            "root": {
                "level": LOG_LEVEL,
                "handlers": ["console", "file"]
            }
        })
