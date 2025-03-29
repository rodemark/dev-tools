import os
import datetime
import gzip
import shutil
from typing import cast, BinaryIO
from logging_tools.singletone import Singleton


class MyLogger(metaclass=Singleton):
    """
    A class for logging messages with support for logging levels,
    colored console output, and automatic log file rotation with archiving.

    Attributes:
        LEVELS (dict): A dictionary mapping logging levels to numeric values.
        COLORS (dict): A dictionary of ANSI codes for colored console output.
    """

    LEVELS = {
        "DEBUG": 1,
        "INFO": 2,
        "WARNING": 3,
        "ERROR": 4,
        "CRITICAL": 5,
    }

    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[41m",  # White text on red background
        "RESET": "\033[0m"  # Reset color
    }

    def __init__(self, log_dir="logs", level="DEBUG"):
        """
        Initializes an instance of MyLogger.
        If an instance already exists, calling __init__ again does not create a new object
        due to the Singleton pattern.
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
        Generates the log file name based on the current date.

        Returns:
            str: The full path to the log file in the format "{log_dir}/log_{current_date}.log".
        """
        return os.path.join(self.log_dir, f"log_{self.current_date}.log")

    def _compress_old_logs(self):
        """
        Archives log files from previous days.

        For each file in the log_dir directory:
            - If the file name starts with "log_" and ends with ".log",
              the date is extracted from the file name.
            - If the date does not match the current one, the file is compressed into a gzip archive,
              and the original log file is deleted.
        """
        for file in os.listdir(self.log_dir):
            if file.startswith("log_") and file.endswith(".log"):
                log_date = file[4:14]  # Extracting date from the file name
                if log_date != self.current_date:
                    log_path = os.path.join(self.log_dir, file)
                    gz_path = log_path + ".gz"

                    with open(log_path, "rb") as f_in:
                        with gzip.open(gz_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, cast(BinaryIO, f_out))

                    os.remove(log_path)
                    print(f"Archived log: {file} → {gz_path}")

    def _write_log(self, level, message):
        """
        Formats and writes a log message if the message level meets the set threshold.

        Parameters:
            level (str): Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
            message (str): The log message text.

        Actions:
            - Checks if the message level meets the minimum threshold.
            - Formats the log message with a timestamp.
            - Displays the message in the console with the corresponding color.
            - Checks if the date has changed and rotates the log file if needed.
            - Writes the message to the log file.
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
        Checks if the current date has changed and, if necessary, rotates the log file.

        Actions:
            - Retrieves today's date in the format MM-DD-YYYY.
            - Compares it with the stored date (self.current_date).
            - If the date has changed:
                - Checks whether the current log file exists.
                - If the file exists, archives it in gzip format by copying the file's contents into an archive and then removing the original.
                - Prints a message indicating that the log file has been archived.
                - Updates self.current_date to today's date.
                - Generates a new log file name for subsequent log entries.
        """
        today = datetime.datetime.now().strftime("%m-%d-%Y")
        if today != self.current_date:
            old_log_file = self.log_file
            if os.path.exists(old_log_file):
                gz_path = old_log_file + ".gz"
                with open(old_log_file, "rb") as f_in:
                    with gzip.open(gz_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(old_log_file)
                print(f"Archived log: {old_log_file} → {gz_path}")

            self.current_date = today
            self.log_file = self._get_log_filename()

    def debug(self, message):
        """
        Logs a message at the DEBUG level.

        Parameters:
            message (str): The message text.
        """
        self._write_log("DEBUG", message)

    def info(self, message):
        """
        Logs a message at the INFO level.

        Parameters:
            message (str): The message text.
        """
        self._write_log("INFO", message)

    def warning(self, message):
        """
        Logs a message at the WARNING level.

        Parameters:
            message (str): The message text.
        """
        self._write_log("WARNING", message)

    def error(self, message):
        """
        Logs a message at the ERROR level.

        Parameters:
            message (str): The message text.
        """
        self._write_log("ERROR", message)

    def critical(self, message):
        """
        Logs a message at the CRITICAL level.

        Parameters:
            message (str): The message text.
        """
        self._write_log("CRITICAL", message)