import os
import logging
from logging import Logger

def setup_logging() -> Logger:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    # Remove any existing handlers
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode='a', encoding='utf-8', delay=False)
        ]
    )
    logger = logging.getLogger(__name__)

    # Debugging statements
    logger.debug(f"Logger handlers after configuration: {root.handlers}")
    logger.debug(f"Logging configured to write to: {log_file}")
    logger.debug("setup_logging function executed")

    # Check if logger has handlers
    if logger.handlers:
        logger.debug(f"Logger has handlers: {logger.handlers}")
    else:
        logger.error("Logger has no handlers configured!")

    return logger