import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(app_name: str = "cerberus", log_level=logging.INFO):
    """Configure and return an app wide logger here"""
    logger = logging.getLogger(app_name)
    
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(log_level)
    
    # Ensure log directory exists
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", "app.log")
    
    #Handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    file_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s %(name)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    #Attach handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger