import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread

from job_queue import JobQueue, Job, Priority, Status
import time
from random import randint, random
from errors import ProcessingError

from src.logger import LoggerFactory

_logger = LoggerFactory.get_logger("Server", os.path.join(os.getcwd(), "log"))


class Server:

    def __init__(self, min_workers: int, max_workers: int, queue: JobQueue):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.job_queue = queue
        self._running = False
        # self.server_thread = Thread(target=self._run)

    def process_job(self, job: Job) -> Job:
        """Process a single job and updates the queue."""
        job.status = Status.PROCESSING
        self.job_queue.sort()
        time.sleep(randint(1, 3))
        # for illustrative purposes about 1 in 5 jobs will error
        if random() < 0.20:
            raise ProcessingError("", job)
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
                    _logger.info(f"Scanning for further jobs...")
                    time.sleep(3)
                else:
                    # process job
                    _logger.info(f"Submitting {job} from the queue...")
                    future = executor.submit(self.process_job, job)
                    futures.add(future)

                # process only completed futures
                done = [f for f in futures if f.done()]
                for future in done:
                    futures.remove(future)
                    try:
                        job = future.result()
                        job.status = Status.FINISHED
                        _logger.info(f"{job}")
                    except ProcessingError as e:
                        e.job.status = Status.ERROR
                        _logger.info(f"{e.job} failed with exception {e}")

        def stop():
            """Stop the server."""
            self._running = False
