
import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_dir='log', log_file='app.log', level=logging.INFO):
    """Function to set up a logger with file rotation in a specified directory"""
    
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Full path for the log file
    log_path = os.path.join(log_dir, log_file)
    
    # Convert 20MB to bytes
    max_bytes = 20 * 1024 * 1024  # 20MB
    
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create handlers
    file_handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=0)
    
    # Create formatters and add it to handlers
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', 
                                  datefmt='%d-%m %H:%M:%S')
    file_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    
    return logger

# Create a global logger instance
logger = setup_logger('global_logger')


def printLogs(msg):
    print(f"{msg}")
