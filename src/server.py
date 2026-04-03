import time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from src.job_queue import JobQueue, Job, Status
from src.errors import ProcessingError
from src.constants import LOGS_DIR
from src.logger import LoggerFactory

_logger_server = LoggerFactory.get_logger("Server", LOGS_DIR)
_logger_worker = LoggerFactory.get_logger("Worker", LOGS_DIR)


class Server:
    """Threaded Server class processing jobs from a queue."""

    def __init__(self, max_workers: int, queue: JobQueue):
        self.max_workers = max_workers
        self.job_queue = queue
        self._running = False
        self.server_thread = Thread(target=self._run, daemon=False)

    def process_job(self, job: Job) -> Job:
        """Process a single job and updates the queue."""
        job.status = Status.PROCESSING
        _logger_worker.info(f"{job}")

        try:
            job.run()
        except RuntimeError as e:
            raise ProcessingError(str(e), job) from e

        return job

    def start(self):
        self.server_thread.start()

    def stop(self):
        """Stop the server."""
        self._running = False

    def _run(self):
        """Run the server. Process jobs from the queue across all workers."""

        self._running = True
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = set()
            while self._running:
                job = self.job_queue.get_next_job()
                if job is None:
                    _logger_server.info(f"Scanning for further jobs...")
                    time.sleep(1)
                else:
                    # Submit to work pool
                    _logger_server.info(f"Submitting {job} from the queue...")
                    future = executor.submit(self.process_job, job)
                    futures.add(future)

                # Process completed jobs to write status reports.
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
