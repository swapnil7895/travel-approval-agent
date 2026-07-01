import logging
import os
import re
from datetime import datetime

# Define the log directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive information like Employee IDs."""
    def filter(self, record):
        # We need to redact sensitive data in the message.
        # We convert the message to string to safely run regex
        original_msg = str(record.getMessage())
        
        # Redact Employee IDs (e.g. EMP2001 -> EMP****)
        redacted_msg = re.sub(r'EMP\d{4}', 'EMP****', original_msg)
        
        # We replace the record's original msg with the redacted one
        record.msg = redacted_msg
        record.args = ()
        return True

def get_logger(name: str) -> logging.Logger:
    """Sets up and returns a configured logger."""
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, return it to avoid duplicate logs
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Create the daily log file name
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"app_{date_str}.log")
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    
    # Attach sensitive data filter
    file_handler.addFilter(SensitiveDataFilter())
    
    # Add handler to the logger
    logger.addHandler(file_handler)
    
    return logger
