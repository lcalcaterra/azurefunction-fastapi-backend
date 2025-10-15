import logging
from logging import StreamHandler

class CustomFormatter(logging.Formatter):
    def format(self, record):
        return super().format(record)
    
TASK_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    logger.propagate = False

    if not logger.handlers:
        # StreamHandler (to log to stdout)
        stream_handler = StreamHandler()
        stream_handler.setFormatter(CustomFormatter(TASK_LOG_FORMAT))
        logger.addHandler(stream_handler)

    logger.setLevel(logging.INFO)

    return logger