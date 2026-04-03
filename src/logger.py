import logging
import os
import sys
from datetime import datetime


class LoggerFactory:
    """Factory for logger instances across applications."""

    @staticmethod
    def get_logger(name: str, log_dir: str) -> logging.Logger:
        """Create and/or return a logger instance."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:

            # Add command line logging
            ch = logging.StreamHandler(stream=sys.stdout)
            logger.addHandler(ch)

            # Add file logger
            log_dir = os.path.join(log_dir, name)
            os.makedirs(log_dir, exist_ok=True)
            fh = logging.FileHandler(os.path.join(log_dir, (datetime.now().strftime("%Y-%m-%d") + ".log")))
            logger.addHandler(fh)

        # TO DO! Add file logging
        return logger
