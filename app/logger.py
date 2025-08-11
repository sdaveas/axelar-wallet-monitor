import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance with consistent formatting
    """
    logger = logging.getLogger(name)
    
    # Only configure the root logger once
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    return logger
