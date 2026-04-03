import logging
import os
import sys
from datetime import datetime


class JobLoggerAdapter(logging.LoggerAdapter):
    """Adds custom format context to log messages."""

    def process(self, msg, kwargs):
        from src.job_queue import Job

        job = self.extra.get("job")
        if isinstance(job, Job):
            msg = f"{job.job_id} | {job.status} | {job.priority} | {msg}"

        # TO DO! Implement the same for Sequence

        return msg, kwargs


class LoggerFactory:
    """Factory for logger instances across applications."""

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
