import logging
import os

# Set up logging configuration
log_file_path = 'logs/app.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Log to specified file
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)

# Test logging
logger.info("This is an info message for testing logging.")
logger.debug("This is a debug message for testing logging.")
logger.error("This is an error message for testing logging.")
