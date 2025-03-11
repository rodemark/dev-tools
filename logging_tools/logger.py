import os
import datetime
import gzip
import shutil
from typing import cast, BinaryIO
from logging_tools.singletone import Singleton


class MyLogger(metaclass=Singleton):
    """
    Класс для логирования сообщений с поддержкой уровней логирования, цветного вывода в консоль
    и автоматической ротации лог-файлов с архивированием.

    Атрибуты:
        LEVELS (dict): Словарь соответствия уровней логирования числовым значениям.
        COLORS (dict): Словарь ANSI-кодов для цветного оформления сообщений в консоли.
    """

    LEVELS = {
        "DEBUG": 1,
        "INFO": 2,
        "WARNING": 3,
        "ERROR": 4,
        "CRITICAL": 5,
    }

    COLORS = {
        "DEBUG": "\033[94m",  # Синий
        "INFO": "\033[92m",  # Зеленый
        "WARNING": "\033[93m",  # Желтый
        "ERROR": "\033[91m",  # Красный
        "CRITICAL": "\033[41m",  # Белый текст на красном фоне
        "RESET": "\033[0m"  # Сброс цвета
    }

    def __init__(self, log_dir="logs", level="DEBUG"):
        """
        Инициализирует экземпляр MyLogger.
        Если экземпляр уже существует, __init__ может быть вызван повторно,
        но в рамках Singleton это не приводит к созданию нового объекта.
        """

        if hasattr(self, '_initialized') and self._initialized:
            return

        self.log_dir = log_dir
        if level.upper() not in self.LEVELS:
            level = "DEBUG"
        self.level = level.upper()
        self.current_date = datetime.datetime.now().strftime("%m-%d-%Y")

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.log_file = self._get_log_filename()
        self._compress_old_logs()
        self._initialized = True

    def _get_log_filename(self):
        """
        Генерирует имя лог-файла на основе текущей даты.

        Возвращает:
            str: Полный путь к лог-файлу в формате "{log_dir}/log_{current_date}.log".
        """
        return os.path.join(self.log_dir, f"log_{self.current_date}.log")

    def _compress_old_logs(self):
        """
        Архивирует лог-файлы за предыдущие дни.

        Для каждого файла в директории log_dir:
            - Если имя файла начинается с "log_" и заканчивается на ".log",
              извлекается дата из имени файла.
            - Если дата не совпадает с текущей, файл архивируется в формате gzip,
              после чего исходный лог-файл удаляется.
        """
        for file in os.listdir(self.log_dir):
            if file.startswith("log_") and file.endswith(".log"):
                log_date = file[4:14]  # Извлечение даты из имени файла
                if log_date != self.current_date:
                    log_path = os.path.join(self.log_dir, file)
                    gz_path = log_path + ".gz"

                    with open(log_path, "rb") as f_in:
                        with gzip.open(gz_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, cast(BinaryIO, f_out))

                    os.remove(log_path)
                    print(f"Архивирован лог: {file} → {gz_path}")

    def _write_log(self, level, message):
        """
        Формирует и записывает сообщение лога, если уровень сообщения соответствует установленному порогу.

        Параметры:
            level (str): Уровень логирования ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
            message (str): Текст лог-сообщения.

        Действия:
            - Проверяет, соответствует ли уровень сообщения минимальному порогу.
            - Формирует строку сообщения с временной меткой.
            - Выводит сообщение в консоль с соответствующим цветом.
            - Проверяет, не изменилась ли дата, и при необходимости ротирует лог-файл.
            - Записывает сообщение в лог-файл.
        """
        if self.LEVELS[level] >= self.LEVELS[self.level]:
            timestamp = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
            log_message = f"[{timestamp}] [{level}] {message}"

            color = self.COLORS.get(level, "")
            print(f"{color}{log_message}{self.COLORS['RESET']}")

            self._rotate_log_file()

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")

    def _rotate_log_file(self):
        """
        Ротирует лог-файл при смене дня.

        Действия:
            - Сравнивает текущую дату с сохраненной датой.
            - Если дата изменилась, обновляет current_date, генерирует новый лог-файл
              и архивирует лог-файлы предыдущих дней.
        """
        today = datetime.datetime.now().strftime("%m-%d-%Y")
        if today != self.current_date:
            self.current_date = today
            self.log_file = self._get_log_filename()
            self._compress_old_logs()

    def debug(self, message):
        """
        Записывает сообщение уровня DEBUG.

        Параметры:
            message (str): Текст сообщения.
        """
        self._write_log("DEBUG", message)

    def info(self, message):
        """
        Записывает сообщение уровня INFO.

        Параметры:
            message (str): Текст сообщения.
        """
        self._write_log("INFO", message)

    def warning(self, message):
        """
        Записывает сообщение уровня WARNING.

        Параметры:
            message (str): Текст сообщения.
        """
        self._write_log("WARNING", message)

    def error(self, message):
        """
        Записывает сообщение уровня ERROR.

        Параметры:
            message (str): Текст сообщения.
        """
        self._write_log("ERROR", message)

    def critical(self, message):
        """
        Записывает сообщение уровня CRITICAL.

        Параметры:
            message (str): Текст сообщения.
        """
        self._write_log("CRITICAL", message)