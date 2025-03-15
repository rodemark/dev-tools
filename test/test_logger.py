import os
import gzip
from datetime import datetime, timedelta
import pytest

from logging_tools.logger import MyLogger


def test_logger_writes_message(tmp_path):
    """
    This test verifies that when a log message is written,
    a file is created and contains the logged message.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger = MyLogger(log_dir=str(log_dir), level="DEBUG")
    test_message = "Test log message :D"
    logger.info(test_message)

    current_date = datetime.now().strftime("%m-%d-%Y")
    log_file = log_dir / f"log_{current_date}.log"
    assert log_file.exists(), "Log file was not created"

    content = log_file.read_text(encoding="utf-8")
    assert test_message in content, "Message was not written to the log file"


def test_compress_old_logs(tmp_path):
    """
    This test verifies that the _compress_old_logs method archives an old log file.
    To test this, we manually create a log file with a date different from the current one.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    old_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")
    old_log_file = log_dir / f"log_{old_date}.log"
    old_log_file.write_text("Old log message", encoding="utf-8")

    logger = MyLogger(log_dir=str(log_dir), level="DEBUG")
    logger._compress_old_logs()

    assert not old_log_file.exists(), "Old log file was not deleted after archiving"
    gz_file = old_log_file.with_suffix(old_log_file.suffix + ".gz")
    assert gz_file.exists(), "Archived file was not created"


def test_logger_rotation_on_date_change(tmp_path):
    """
    This test verifies that when the date changes (simulating log file rotation),
    a new log file is created, and the old one is archived.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger = MyLogger(log_dir=str(log_dir), level="DEBUG")
    logger.info("Message before rotation")

    old_date = logger.current_date
    old_log_file = log_dir / f"log_{old_date}.log"
    assert old_log_file.exists(), "Original log file not found"

    logger.current_date = "01-01-2000"
    logger.info("Message after rotation")

    new_date = datetime.now().strftime("%m-%d-%Y")
    new_log_file = log_dir / f"log_{new_date}.log"
    assert new_log_file.exists(), "New log file was not created during rotation"

    gz_file = old_log_file.with_suffix(old_log_file.suffix + ".gz")
    assert gz_file.exists(), "Old log file was not archived during rotation"
