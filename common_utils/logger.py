import logging
import os
import time

# Create a "logs" directory if it doesn't exist
if not os.path.exists('logs'):
    os.mkdir('logs')

# Generate a timestamp for the log file in UTC
current_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.gmtime())
log_file_name = f'logs/app_{current_time}.log'

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a formatter to include a timestamp in UTC
formatter = logging.Formatter('%(asctime)s [UTC] - %(levelname)s - %(message)s')

# Create a file handler for all log levels in a new log file
log_handler = logging.FileHandler(log_file_name)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(formatter)
logging.Formatter.converter = time.gmtime

# Create a stream handler to print log messages to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(log_handler)
logger.addHandler(console_handler)
