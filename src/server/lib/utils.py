from datetime import time
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


def err_log(func_name: str, e: Exception, filename: str) -> None:
    """Log an exception to the specified file."""
    err_name = str(type(e)).split("'")[1]
    log(f"[{func_name}] {err_name}: {e}", filename, 'ERROR')


def parse_time(time_str: str) -> time:
    """Turns a string time to a `datetime.time` object (e.g, "08:00" -> `time(8, 0)`)."""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return time(hours, minutes)
    except ValueError:
        raise ValueError(f'Invalid time format: "{time_str}". Expected format is "HH:MM".')


def parse_schedule(schedule: list[list[str]]) -> list[list[int]]:
    """Converts the given schedule from being a 2D string array to a 2D integer array."""
    # Flatten the nested list into a single list of strings
    flattened = [item for sublist in schedule for item in sublist]

    # Initialize the result and a temporary list to hold each row
    result, current_row = [], []
    number_buffer = ''  # Buffer to hold multi-digit numbers

    for token in flattened:
        if token == '{':  # Start of a new row
            current_row = []
        elif token == '}':  # End of the current row
            if number_buffer:  # Append the last buffered number to the row
                current_row.append(int(number_buffer))
                number_buffer = ''
            if current_row:  # Append the completed row to the result
                result.append(current_row)
                current_row = []
        elif token.isdigit():  # Build the number buffer for multi-digit numbers
            number_buffer += token
        elif token == ',' and number_buffer:  # Comma separates numbers
            current_row.append(int(number_buffer))
            number_buffer = ''  # Reset the buffer for the next number
    return result


def todict(obj: object):
    """Converts a SQLAlchemy object to a dictionary."""
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


def todicts(objs: list[object]):
    """Converts a list of SQLAlchemy objects to a list of dictionaries."""
    return [todict(obj) for obj in objs]