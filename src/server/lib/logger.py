import logging
import os
from src.server.lib.constants import CURRENT_DIR, ENABLE_LOGGING

# Initialize log directory
LOG_DIR = os.path.join(CURRENT_DIR, "../logs/")
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str, filename: str, level: str = "INFO") -> logging.Logger:
    """
    Get a logger with a specific name and file handler.

    ---
    :param name: The name of the logger.
    :param filename: The log file name (without the .log extension).
    :param level: The logging level (INFO, WARNING, etc.).
    """
    if not ENABLE_LOGGING:
        return None  # Disable logging if the environment variable is set to False

    logger = logging.getLogger(name)

    if not logger.hasHandlers():  # Avoid adding duplicate handlers
        level = logging._nameToLevel[level.upper()]
        log_file = os.path.join(LOG_DIR, f"{filename}.log")
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logger.setLevel(level)
        logger.addHandler(file_handler)

    return logger


def log(msg: str, filename: str, level: str = "INFO") -> None:
    """
    Write a log message to the specified logger and file.

    ---
    :param msg: The message to log.
    :param filename: The logging file name (without the .log extension).
    :param level: The logging level (INFO, WARNING, etc.).
    """
    logger = get_logger(name=filename, filename=filename, level=level)
    if logger:
        logger.log(logging._nameToLevel[level.upper()], msg)


def err_log(func_name: str, e: Exception, filename: str) -> None:
    """
    Log an error to the specified file.

    ---
    :param func_name: The name of the function where the error occurred.
    :param e: The exception to log.
    :param filename: The logging file name (without the .log extension).
    """
    err_name = str(type(e)).split("'")[1]
    log(f"[{func_name}] {err_name}: {e}", filename, "ERROR")