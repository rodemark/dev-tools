import os
import datetime
import gzip
import shutil
from dev_tools.logging_tools.singletone import Singleton


class MyLogger(metaclass=Singleton):
    """
    Class for logging messages with support for different logging levels,
    colored console output, and automatic log rotation with archiving.
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
        Initialize the MyLogger instance.
        If an instance already exists (Singleton), subsequent calls to __init__ will have no effect.
        """
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.log_dir = log_dir
        self.level = level.upper() if level.upper() in self.LEVELS else "DEBUG"
        self.current_date = self._today()

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.log_file = self._get_log_filename()
        self._compress_old_logs()
        self._initialized = True

    def _today(self) -> str:
        """Return the current date in MM-DD-YYYY format."""
        return datetime.datetime.now().strftime("%m-%d-%Y")

    def _get_log_filename(self) -> str:
        """
        Generate the log filename based on the current date.

        Returns:
            str: The full path to the log file in the format "{log_dir}/log_{current_date}.log".
        """
        return os.path.join(self.log_dir, f"log_{self.current_date}.log")

    def _archive_log_file(self, file_path: str) -> None:
        """
        Compress the specified log file into gzip format and remove the original file.

        Args:
            file_path (str): Path to the log file.
        """
        gz_path = file_path + ".gz"
        with open(file_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(file_path)
        print(f"Archived log: {os.path.basename(file_path)} → {gz_path}")

    def _compress_old_logs(self) -> None:
        """
        Archive log files that do not match the current date.
        For each file in log_dir starting with "log_" and ending with ".log",
        the file is archived if its date does not match today's date.
        """
        for filename in os.listdir(self.log_dir):
            if filename.startswith("log_") and filename.endswith(".log"):
                log_date = filename[4:14]  # Extract date from filename
                if log_date != self.current_date:
                    log_path = os.path.join(self.log_dir, filename)
                    self._archive_log_file(log_path)

    def _rotate_log_file(self) -> None:
        """
        Check if the date has changed. If so, archive the current log file
        and update the log file name for new log entries.
        """
        today = self._today()
        if today != self.current_date:
            if os.path.exists(self.log_file):
                self._archive_log_file(self.log_file)
            self.current_date = today
            self.log_file = self._get_log_filename()

    def _write_log(self, level: str, message: str) -> None:
        """
        Format and write a log message if its level meets the threshold.

        Args:
            level (str): Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
            message (str): The log message text.
        """
        if self.LEVELS[level] >= self.LEVELS[self.level]:
            timestamp = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
            log_message = f"[{timestamp}] [{level}] {message}"

            color = self.COLORS.get(level, "")
            print(f"{color}{log_message}{self.COLORS['RESET']}")

            self._rotate_log_file()

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")

    def debug(self, message: str) -> None:
        """Log a message at the DEBUG level."""
        self._write_log("DEBUG", message)

    def info(self, message: str) -> None:
        """Log a message at the INFO level."""
        self._write_log("INFO", message)

    def warning(self, message: str) -> None:
        """Log a message at the WARNING level."""
        self._write_log("WARNING", message)

    def error(self, message: str) -> None:
        """Log a message at the ERROR level."""
        self._write_log("ERROR", message)

    def critical(self, message: str) -> None:
        """Log a message at the CRITICAL level."""
        self._write_log("CRITICAL", message)