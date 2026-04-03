import json
import os
import threading
from enum import Enum
from typing import Optional, List, Dict

from src.constants import LOGS_DIR, JOBS_DIR
from src.file_parser import File
from datetime import datetime

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
    """Represents a job in the job queue."""

    DEFAULT_PRIORITY = Priority.MEDIUM
    _jobs_total = 0

    def __init__(
        self,
        sequence: List[File],
        priority: Optional[Priority] = DEFAULT_PRIORITY,
        status: Optional[Status] = Status.SUBMITTED,
    ):
        self.sequence = sequence
        self.priority = priority or self.DEFAULT_PRIORITY
        self.submit_time = datetime.now()
        self.status = status
        Job._jobs_total = Job._jobs_total + 1
        self.job_id = Job._jobs_total

    def save_status_report(self, error_message: Optional[str] = None):
        """ "Store a json with a job report."""

        with open(os.path.join(JOBS_DIR, f"job_status_{self.job_id}.json"), "w") as status_report:
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

    def __init__(self, queue: Optional[List[Job]] = None):
        self._queue: List[int] = []
        self._job_registry: Dict[int, Job] = {}
        self.lock = threading.Lock()
        if queue:
            for job in queue:
                self.add(job)

    def generate_id(self, sequence):
        pass

    def add(self, job: Job):
        with self.lock:
            job.status = Status.QUEUED
            self._job_registry[job.job_id] = job
            self._queue.append(job.job_id)
            _logger.debug(f"Added job: {job.job_id} to queue.")
        self.sort()

    def remove_from_queue(self, job: Job):
        with self.lock:
            _logger.debug(f"Removed job: {job.job_id} from queue.")
            self._queue.remove(job)

    def sort(self):
        """Sort the jobs in the queue. First by highest priority, then by date."""
        with self.lock:
            unsorted_jobs = self._fetch_jobs_from_ids(self._queue)
            sorted_jobs = sorted(
                unsorted_jobs, key=lambda job: (job.status.value, -job.priority.value, job.submit_time), reverse=True
            )
            self._queue = [job.job_id for job in sorted_jobs]

    def get_next_job(self) -> Job | None:
        with self.lock:
            job = None
            if len(self._queue) > 0:
                job_id = self._queue.pop()
                job = self._job_registry[job_id]
            return job

    def _fetch_jobs_from_ids(self, ids: List[int]) -> List[Job]:
        """Given a list of job ids it returns a list of job instances."""

        return [self._job_registry[i] for i in ids]

    def queue(self) -> List[int]:
        return self._queue

    def __str__(self):
        str_queue = ""
        for job_id in self._queue:
            str_queue += str(job_id) + ", "
        return str_queue
