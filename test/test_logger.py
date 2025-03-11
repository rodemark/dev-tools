import os
import gzip
from datetime import datetime, timedelta
import pytest

from logging_tools.logger import MyLogger


def test_logger_writes_message(tmp_path):
    """
    Тест проверяет, что при записи лог-сообщения создаётся файл,
    и в файле содержится записанное сообщение.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger = MyLogger(log_dir=str(log_dir), level="DEBUG")
    test_message = "Test log message :D"
    logger.info(test_message)

    current_date = datetime.now().strftime("%m-%d-%Y")
    log_file = log_dir / f"log_{current_date}.log"
    assert log_file.exists(), "Лог-файл не был создан"

    content = log_file.read_text(encoding="utf-8")
    assert test_message in content, "Сообщение не записано в лог-файл"


def test_compress_old_logs(tmp_path):
    """
    Тест проверяет, что метод _compress_old_logs архивирует старый лог-файл.
    Для этого вручную создаём лог-файл с датой, отличной от текущей.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    old_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")
    old_log_file = log_dir / f"log_{old_date}.log"
    old_log_file.write_text("Old log message", encoding="utf-8")

    logger = MyLogger(log_dir=str(log_dir), level="DEBUG")
    logger._compress_old_logs()

    assert not old_log_file.exists(), "Старый лог-файл не удалён после архивирования"
    gz_file = old_log_file.with_suffix(old_log_file.suffix + ".gz")
    assert gz_file.exists(), "Архивный файл не создан"


def test_logger_rotation_on_date_change(tmp_path):
    """
    Тест проверяет, что при изменении даты (симуляция ротации лог-файла)
    создаётся новый лог-файл, а старый архивируется.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger = MyLogger(log_dir=str(log_dir), level="DEBUG")
    logger.info("Message before rotation")

    old_date = logger.current_date
    old_log_file = log_dir / f"log_{old_date}.log"
    assert old_log_file.exists(), "Исходный лог-файл не найден"

    logger.current_date = "01-01-2000"
    logger.info("Message after rotation")

    new_date = datetime.now().strftime("%m-%d-%Y")
    new_log_file = log_dir / f"log_{new_date}.log"
    assert new_log_file.exists(), "Новый лог-файл не создан при ротации"

    gz_file = old_log_file.with_suffix(old_log_file.suffix + ".gz")
    assert gz_file.exists(), "Старый лог-файл не архивирован при ротации"
