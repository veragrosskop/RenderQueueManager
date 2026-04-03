import os
import random
import shutil
import time
from typing import Tuple, Dict

from src.logger import LoggerFactory
from src.constants import LOGS_DIR, SAMPLE_DIR, JOBS_DIR
from src.file_parser import FileSequenceParser
from src.job_queue import Priority, Job, JobQueue
from src.server import Server


def _random_missing_frames(directory: str, name: str, chance: int, frame_range: Tuple[int, int], file_extension: str):
    """Generate a sequence of files with missing frames by chance."""

    os.makedirs(directory, exist_ok=True)
    for i in range(frame_range[0], frame_range[1] + 1):
        # skip a chanced amount of frames, to simulate random missing frames
        if random.randint(0, 100) < chance:
            continue
        else:
            filename = f"{name}_{str(i).zfill(4)}{file_extension}"
            file_path = os.path.join(directory, filename)
            if not (os.path.exists(file_path)):
                # write an empty file
                with open(file_path, "wb") as f:
                    pass


def _generate_test_data(base_dir: str, directory_count: int, chance: int) -> Dict[str, Tuple[int, int]]:
    """
    Generates a directory with sample data. It will create a given an amount(directory_count)
    of complete as well as the same number of incomplete sequences.
    For the incomplete sequences a random frame will be deleted by the given chance.
    """

    shutil.rmtree(base_dir)

    sequences = {}
    for i in range(0, directory_count):

        # create complete sequences
        directory = os.path.join(base_dir, f"complete_sequences{i}")
        frame_range = (1001, 1005)
        sequences[directory] = frame_range
        extension = random.choice([".png", ".exr", ".tiff"])
        _random_missing_frames(directory, "render", 0, frame_range, extension)

        # create incomplete sequences
        directory = os.path.join(base_dir, f"incomplete_sequences{i}")
        frame_range = (1001, 1010)
        sequences[directory] = frame_range
        extension = random.choice([".png", ".exr", ".tiff"])
        _random_missing_frames(directory, "render", chance, frame_range, extension)

        # create multiple sequences in same directory
        directory = os.path.join(base_dir, f"multiple_sequences")
        frame_range = (1001, 1010)
        sequences[directory] = frame_range
        extension = random.choice([".png", ".exr", ".tiff"])
        _random_missing_frames(directory, f"rendercomplete{i}", 0, frame_range, extension)
        _random_missing_frames(directory, f"renderincomplete{i}", chance * 2, frame_range, extension)
    return sequences


if __name__ == "__main__":
    # initialize directories
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    shutil.rmtree(JOBS_DIR, ignore_errors=True)
    os.makedirs(JOBS_DIR, exist_ok=True)

    logger = LoggerFactory.get_logger("main", LOGS_DIR)

    # generate sample data
    logger.info(f"Generating Sample data in base_dir: {SAMPLE_DIR}")
    sequences = _generate_test_data(
        SAMPLE_DIR,
        10,
        20,
    )
    for key, value in sequences.items():
        logger.info(f"\t----- {str.replace(key, (SAMPLE_DIR + "\\"), "")}, frame-range: {value}")
    logger.info(f"Finished Generating Sample data.\n")

    # Parse Sequences
    logger.info(f"Parsing File Sequences:")
    complete = []
    incomplete = []
    for directory, frame_range in sequences.items():
        sequencer = FileSequenceParser(directory, frame_range)
        sequences_report = sequencer.generate_report()
        for name, sequence_report in sequences_report.items():
            if sequence_report["status"] == "incomplete":
                incomplete.append(directory)
            else:
                complete.append(directory)
    logger.info(f"Finished Parsing File Sequences.")
    logger.info(f"{len(complete)} Complete Sequences: {complete}")
    logger.info(f"{len(incomplete)} Incomplete Sequences: {incomplete}")

    # Initialize queue and server.
    queue = JobQueue()
    server = Server(max_workers=5, queue=queue)

    # Initialize job instances to push onto the queue.
    for directory, frame_range in sequences.items():
        sequencer = FileSequenceParser(directory, frame_range)
        for name, sequence in sequencer.sequences.items():
            job = Job(
                queue.get_next_job_id(),
                sequence,
                priority=random.choice([Priority.HIGH, Priority.MEDIUM, Priority.LOW]),
            )
            queue.add(job)

    # Start the server
    server.start()

    # Sleep for some time and submit more jobs
    time.sleep(20)
    logger.info(f"Submitting further jobs to server.")
    for directory, frame_range in sequences.items():
        sequencer = FileSequenceParser(directory, frame_range)
        for name, sequence in sequencer.sequences.items():
            job = Job(
                queue.get_next_job_id(),
                sequence,
                priority=random.choice([Priority.HIGH, Priority.MEDIUM, Priority.LOW]),
            )
            queue.add(job)

    # Join the server thread to ensure the python process is not killed preemptively.
    server.server_thread.join()
