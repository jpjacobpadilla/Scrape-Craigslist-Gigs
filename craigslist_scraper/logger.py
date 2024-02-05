import logging
import logging.config
import os


def _get_next_log_number(log_directory: str) -> int:
    """ Helper method for logger configure_logger(). """
    log_files = [f for f in os.listdir(log_directory) if f.startswith("log_") and f.endswith(".log")]
    max_number = 0

    for file in log_files:
        parts = file.replace("log_", "").replace(".log", "")
        try:
            number = int(parts)
            max_number = max(max_number, number)
        except ValueError:
            continue

    return max_number + 1


def configure_logger() -> None:
    """ Set up the logger. """            
    log_directory = "./logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_number = _get_next_log_number(log_directory)
    log_filename = os.path.join(log_directory, f"log_{log_number}.log")

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'file_handler': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': log_filename,
                'mode': 'w',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',  # Use standard output
            },
        },
        'root': {
            'handlers': ['file_handler', 'console'],
            'level': 'DEBUG',
        },
    }

    logging.config.dictConfig(logging_config)
