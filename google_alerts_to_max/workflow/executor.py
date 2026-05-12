import traceback
import random
import time
import math
from concurrent.futures import ThreadPoolExecutor
from .errors import SuccessConditionFailedException, ExecutionFailedException
from .models import SuccessAttemptResult, ErrorAttempt


class AttemptExecutor:
    def __init__(self) -> None:
        self.__pool = ThreadPoolExecutor()

    # pylint: disable=too-many-positional-arguments
    def try_execute(
        self,
        target_func: callable,
        attempts: int = 10,
        timeout_secs: int = 30,
        try_wait_secs: int = 1,
        success_condition: callable = None,
    ) -> SuccessAttemptResult:
        """
        Попробовать запустить вызываемое

        :param target_func: Вызываемое (функция/ламбада)
        :param attempts: Максимальное количество попыток (по умолчанию: 10)
        :param timeout_secs: Таймаут (в секундах) (по умолчанию: 30 секунд)
        :param try_wait_secs: Время ожидания перед следующей попыткой
            (в секундах) (по умолчанию: одна секунда)
        :param success_condition: Функция, которая получает результат
            вызываемого и возвращает булевое значение

        :returns: Успешный результат вызываемого
        """

        start_time = time.time()
        errors = []

        for attempt in range(1, attempts + 1):
            try:
                # выполняем вызываемое
                future = self.__pool.submit(target_func)
                result = future.result(timeout=timeout_secs)

                # исполняем условие, если оно представлено
                if success_condition and not success_condition(result):
                    raise SuccessConditionFailedException(
                        "Провалено исключение успешного выполнения", result=result
                    )

                # возвращаем успешный результат
                return SuccessAttemptResult(
                    attempts_used=attempt,
                    time_taken_secs=math.floor(time.time() - start_time),
                    errors=errors,
                    result=result,
                )
            except (KeyboardInterrupt, SystemExit):  # pylint: disable=try-except-raise
                raise  # пропускаем такую ошибку
            except Exception as e:
                # добавляем ошибку в список
                error = ErrorAttempt(
                    exception=e,
                    traceback=traceback.format_exc(),
                    attempt=attempt,
                    timestamp=math.floor(time.time()),
                )
                errors.append(error)

                # ждем некоторое время до следующей попытки
                if attempt < attempts:
                    backoff = try_wait_secs * attempt
                    jitter = random.uniform(0, backoff * 0.3)

                    time.sleep(backoff + jitter)

        # возвращаем ошибку, если все попытки были провалены
        raise ExecutionFailedException(
            "Запуск вызываемого провален",
            attempts=attempts,
            time_taken_secs=math.floor(time.time() - start_time),
            errors=errors,
        )
