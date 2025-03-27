"""Logging utilities for Groot CLI."""

import logging
import os
import sys
from typing import Optional
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

from groot.config import config

# Create console for rich output
console = Console()

# Define log levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None):
    """Set up logging for Groot CLI."""
    # Get log level from config or parameter
    level_name = log_level or config.get("log_level", "info")
    level = LOG_LEVELS.get(level_name.lower(), logging.INFO)

    # Create logger
    logger = logging.getLogger("groot")
    logger.setLevel(level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        console=console,
        show_time=False,
        show_path=False
    )
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # Create file handler if log file is specified
    if log_file or config.get("log_file"):
        file_path = log_file or config.get("log_file")
        log_dir = os.path.dirname(file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(file_handler)

    return logger

def get_logger(name: str = "groot"):
    """Get a logger instance."""
    return logging.getLogger(name)

# Set up default logger
logger = setup_logging()