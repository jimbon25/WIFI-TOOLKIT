"""
Centralized logging module for wifi-tool.
Replaces custom _log functions throughout codebase.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for terminal output."""
    
    COLORS = {
        'DEBUG': '\033[0;36m',    # Cyan
        'INFO': '\033[0;32m',     # Green
        'WARNING': '\033[1;33m',  # Yellow
        'ERROR': '\033[0;31m',    # Red
        'CRITICAL': '\033[1;31m', # Bright Red
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if not hasattr(record, 'color_levelname'):
            levelname = record.levelname
            color = self.COLORS.get(levelname, self.RESET)
            record.color_levelname = f"{color}{levelname}{self.RESET}"
        
        return super().format(record)


def setup_logger(
    name: str,
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_dir: str = '/tmp/wifi-tool/'
) -> logging.Logger:
    """
    Set up a logger instance with both console and file output.
    
    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional specific log file path
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    formatted = ColoredFormatter(
        fmt='%(color_levelname)-8s [%(asctime)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatted)
    logger.addHandler(console_handler)
    
    # File handler if log file specified
    if log_file or log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            
            if not log_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                log_file = os.path.join(log_dir, f'wifi_tool_{timestamp}.log')
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10485760,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            file_formatter = logging.Formatter(
                fmt='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {e}")
    
    return logger


# Global logger instances for different components
wifi_logger = setup_logger('wifi-tool.main')
network_logger = setup_logger('wifi-tool.network')
attack_logger = setup_logger('wifi-tool.attack')
security_logger = setup_logger('wifi-tool.security')
debug_logger = setup_logger('wifi-tool.debug', log_level=logging.DEBUG)


class LoggingMixin:
    """Mixin class to provide logging capability to any class."""
    
    def __init__(self, logger_name: str = 'wifi-tool'):
        self._logger = logging.getLogger(logger_name)
    
    def log_debug(self, message: str):
        """Log debug message."""
        self._logger.debug(message)
    
    def log_info(self, message: str):
        """Log info message."""
        self._logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message."""
        self._logger.warning(message)
    
    def log_error(self, message: str):
        """Log error message."""
        self._logger.error(message)
    
    def log_critical(self, message: str):
        """Log critical message."""
        self._logger.critical(message)
    
    def _log(self, level: str, message: str):
        """Legacy method for compatibility with existing code."""
        level_map = {
            'DEBUG': self._logger.debug,
            'INFO': self._logger.info,
            'WARNING': self._logger.warning,
            'ERROR': self._logger.error,
            'CRITICAL': self._logger.critical,
        }
        log_func = level_map.get(level.upper(), self._logger.info)
        log_func(message)


# Configure root logger to suppress excessive logging from dependencies
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
