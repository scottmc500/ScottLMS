"""
Logging configuration for ScottLMS
"""

import logging
import sys
from enum import Enum
from typing import Optional, Union


class LogLevel(Enum):
    """Logging levels enum"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    @property
    def level_value(self) -> int:
        """Get the numeric logging level value"""
        return getattr(logging, self.value)


def setup_logging(level: Optional[Union[str, LogLevel]] = LogLevel.INFO) -> None:
    """
    Setup basic logging configuration
    
    Args:
        level: Logging level (can be string or LogLevel enum)
    """
    if isinstance(level, LogLevel):
        log_level = level.level_value
    elif isinstance(level, str):
        log_level = getattr(logging, level.upper())
    else:
        log_level = LogLevel.INFO.level_value
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
