from datetime import date, time
import logging, os
from src.server.lib.constants import ENABLE_LOGGING, locate

# Initialize log directory
LOG_DIR = locate('../logs/')
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str, filename: str, level: str = 'INFO') -> logging.Logger:
    """Get a logger with a specific name and file handler."""
    if not ENABLE_LOGGING: return None
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


def log(msg: str, filename: str, level: str = 'INFO') -> None:
    """Write a log message with the specified file and level."""
    logger = get_logger(name=filename, filename=filename, level=level)
    if logger: logger.log(logging._nameToLevel[level.upper()], msg)


def errlog(func_name: str, e: Exception, filename: str) -> None:
    """Log an exception to the specified file."""
    err_name = str(type(e)).split("'")[1]
    log(f"[{func_name}] {err_name}: {e}", filename, 'ERROR')


def parse_date(date_str: str):
    """Turns a string date to a `datetime.date` object (e.g, "2024-03-29" -> `date(2024, 3, 29)`)."""
    try:
        year, month, day = map(int, date_str.split('-'))
        return date(year, month, day)
    except ValueError:
        raise ValueError(f'Invalid date format: "{date_str}". Expected format is "YYYY-MM-DD".')


def parse_time(time_str: str) -> time:
    """Turns a string time to a `datetime.time` object (e.g, "08:00" -> `time(8, 0)`)."""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return time(hours, minutes)
    except ValueError:
        raise ValueError(f'Invalid time format: "{time_str}". Expected format is "HH:MM".')


def todict(obj: object):
    """Converts a SQLAlchemy object to a dictionary."""
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


def todicts(objs: list[object]):
    """Converts a list of SQLAlchemy objects to a list of dictionaries."""
    return [todict(obj) for obj in objs]