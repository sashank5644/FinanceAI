"""Logging configuration for the application."""

import logging
import sys
from rich.logging import RichHandler
from rich.console import Console

console = Console()


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with Rich formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create Rich handler
    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True
    )
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(message)s",
        datefmt="[%X]"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger
