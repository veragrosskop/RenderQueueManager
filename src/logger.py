import logging
import os
import sys
from datetime import datetime


class LoggerFactory:
    """Factory for logger instance creation."""

    DEFAULT_FORMAT_CONSOLE = " %(asctime)s | %(name)-7s | %(levelname)s | %(message)s"
    DEFAULT_FORMAT_FILE = " %(asctime)s | %(levelname)s | %(message)s"

    @staticmethod
    def get_logger(name: str, log_dir: str) -> logging.Logger:
        """Create and/or return a logger instance."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            formatter_console = logging.Formatter(LoggerFactory.DEFAULT_FORMAT_CONSOLE)

            # Add command line logging
            ch = logging.StreamHandler(stream=sys.stdout)
            ch.setFormatter(formatter_console)
            logger.addHandler(ch)

            formatter_file = logging.Formatter(LoggerFactory.DEFAULT_FORMAT_FILE)

            # Add file logger
            log_dir = os.path.join(log_dir, name)
            os.makedirs(log_dir, exist_ok=True)
            fh = logging.FileHandler(os.path.join(log_dir, (datetime.now().strftime("%Y-%m-%d") + ".log")))
            fh.setFormatter(formatter_file)
            logger.addHandler(fh)

        return logger
