from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.interval import IntervalTrigger
from google_alerts_to_max.workflow import Workflow
from datetime import datetime, timezone
from .config import (
    MAX_TOKEN,
    MAX_USER_ID,
    MAX_CHAT_ID,
    GMAIL_CREDENTIALS_USER,
    GMAIL_CREDENTIALS_PASS,
    FILTER_DB_PATH
)


class Program:
    """
    Программа. Настраивает планировщик и время от времени
    запускает рабочий процесс
    """

    def __init__(self):
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

        # создание планировщика
        self.__scheduler = BlockingScheduler(
            jobstores={"default": MemoryJobStore()},
            executors={"default": ThreadPoolExecutor()},
            job_defaults={
                "coalesce": False,
                "max_instances": 1
            }
        )

    def main(self) -> None:
        """
        Основная функция программы
        """

        # настраиваем планировщик и запускаем его
        self.__scheduler.add_job(
            lambda: self.__workflow.run(),
            IntervalTrigger(
                hours=4,
                start_time=datetime.now(timezone.utc)
            ),
        )

        try:
            self.__scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass
