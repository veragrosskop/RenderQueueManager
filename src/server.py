import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread

from job_queue import JobQueue, Job, Priority, Status
import time
from random import randint, random
from errors import ProcessingError
from src.constants import LOGS_DIR

from src.logger import LoggerFactory

_logger_server = LoggerFactory.get_logger("Server", LOGS_DIR)
_logger_worker = LoggerFactory.get_logger("Worker", LOGS_DIR)


class Server:

    def __init__(self, max_workers: int, queue: JobQueue):
        self.max_workers = max_workers
        self.job_queue = queue
        self._running = False
        # self.server_thread = Thread(target=self._run)

    def process_job(self, job: Job) -> Job:
        """Process a single job and updates the queue."""
        job.status = Status.PROCESSING
        _logger_worker.info(f"{job}")
        self.job_queue.sort()
        time.sleep(randint(1, 3))
        # for illustrative purposes about 1 in 5 jobs will error
        if random() < 0.20:
            raise ProcessingError("Failed due to random chance...", job)
        return job

    def start(self):
        # self.server_thread.start()
        self._run()

    def _run(self):
        """Run the server. Process jobs from the queue across all workers."""

        self._running = True
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = set()
            while self._running:
                # get next in cue
                job = self.job_queue.get_next_job()
                if job is None:
                    _logger_server.info(f"Scanning for further jobs...")
                    time.sleep(3)
                else:
                    # process job
                    _logger_server.info(f"Submitting {job} from the queue...")
                    future = executor.submit(self.process_job, job)
                    futures.add(future)

                # process only completed futures
                done = [f for f in futures if f.done()]
                for future in done:
                    futures.remove(future)
                    try:
                        job = future.result()
                        job.status = Status.FINISHED
                        job.save_status_report()
                        _logger_worker.info(f"{job}")
                    except ProcessingError as e:
                        e.job.status = Status.ERROR
                        e.job.save_status_report(error_message=str(e))
                        _logger_worker.info(f"{e.job}: {e}")

        def stop():
            """Stop the server."""
            self._running = False
