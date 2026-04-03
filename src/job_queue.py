import heapq
import json
import os
import random
import threading
import time
from enum import Enum
from datetime import datetime
from typing import Optional, List, Tuple

from src.constants import LOGS_DIR, JOBS_DIR
from src.errors import ProcessingError
from src.file_parser import File
from src.logger import LoggerFactory

_logger = LoggerFactory.get_logger("Queue", LOGS_DIR)


class Priority(Enum):
    """Represents the priority of a job."""

    LOW = 0
    MEDIUM = 50
    HIGH = 100


class Status(Enum):
    """Represents the status of a job."""

    QUEUED = "0"
    SUBMITTED = "1"
    PROCESSING = "2"
    ERROR = "3"
    FINISHED = "4"


class Job:
    """Represents a job executing work."""

    DEFAULT_PRIORITY = Priority.MEDIUM

    def __init__(
        self,
        job_id: int,
        sequence: List[File],
        priority: Optional[Priority] = DEFAULT_PRIORITY,
        status: Optional[Status] = Status.SUBMITTED,
    ):
        self.submit_time = datetime.now()

        self.sequence = sequence
        self.priority = priority or self.DEFAULT_PRIORITY
        self.status = status
        self.job_id = job_id

    def run(self):
        time.sleep(random.randint(1, 3))
        # for illustrative purposes about 1 in 5 jobs will error,
        # we could also make missing frame sequences fail alternatively.
        if random.random() < 0.20:
            raise RuntimeError("Failed due to random chance...")

    def save_status_report(self, error_message: Optional[str] = None):
        """Write the jobs' current status to a json file. Should be called at execution end."""

        with open(os.path.join(JOBS_DIR, f"job_report_{self.job_id}.json"), "w") as status_report:
            json.dump(
                {
                    "job_id": str(self.job_id),
                    "submit_time": str(self.submit_time),
                    "status": str(self.status),
                    "priority": str(self.priority),
                    "error_message": error_message if error_message else "",
                },
                fp=status_report,
                indent=4,
            )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"job: {self.job_id}, {str(self.priority)}, {self.status}"


class JobQueue:
    """Represents a queue of jobs."""

    def __init__(self, jobs: Optional[List[Job]] = None):
        self._heap: List[Job] = []
        self.lock = threading.Lock()
        self._job_count = 0

        if jobs:
            for job in jobs:
                self.add(job)

    def _priority(self, job: Job) -> Tuple[int, int, datetime]:
        """Defines sorting priority of the heap."""
        return (
            job.status.value,
            -job.priority.value,
            job.submit_time,
        )

    def add(self, job: Job):
        """Adds a job to the queue and inserts it into the correct spot."""
        with self.lock:
            job.status = Status.QUEUED
            entry = (*self._priority(job), job)
            heapq.heappush(self._heap, entry)
            _logger.debug(f"Added job: {job.job_id} to queue.")

    def get_next_job_id(self) -> int:
        value = self._job_count
        self._job_count += 1
        return value

    def get_next_job(self) -> Job | None:
        """Pops an item from the queue and reorders it."""
        with self.lock:
            if not self._heap:
                return None

            _, _, _, job = heapq.heappop(self._heap)
            return job

    def __str__(self):
        str_queue = ""
        for _, _, _, job in self._heap:
            str_queue += str(job.job_id) + ", "
        return str_queue
