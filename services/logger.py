import logging
from logging.handlers import RotatingFileHandler

class SafeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'user_id'):
            record.user_id = "N/A"
        if not hasattr(record, 'command'):
            record.command = "N/A"
        return super().format(record)


logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = RotatingFileHandler(
        "bot.log",
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding="utf-8"
    )

    formatter = SafeFormatter(
        "%(asctime)s | %(levelname)-8s | User:%(user_id)-10s | Command:%(command)-15s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def log_info(user_id: int | None = None, command: str | None = None, message: str = ""):
    logger.info(message, extra={"user_id": user_id or "N/A", "command": command or "N/A"})


def log_warning(user_id: int | None = None, command: str | None = None, message: str = ""):
    logger.warning(message, extra={"user_id": user_id or "N/A", "command": command or "N/A"})


def log_error(user_id: int | None = None, command: str | None = None, error: Exception | str = ""):
    logger.error(str(error), extra={"user_id": user_id or "N/A", "command": command or "N/A"})