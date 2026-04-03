import logging
import os
import random
from typing import Tuple, Dict
from logger import LoggerFactory
from src.file_parser import FileSequenceParser


def _random_missing_frames(directory: str, chance: int, frame_range: Tuple[int, int], file_extension: str):
    """Generate a sequence of files with missing frames by chance."""

    os.makedirs(directory, exist_ok=True)
    for i in range(frame_range[0], frame_range[1] + 1):
        # skip a chanced amount of frames, to simulate random missing frames
        if random.randint(0, 100) < chance:
            continue
        else:
            filename = f"render_{str(i).zfill(4)}{file_extension}"
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

    sequences = {}
    for i in range(0, directory_count):

        # create complete sequences
        directory = os.path.join(base_dir, f"complete_sequences{i}")
        frame_range = (1001, 1100)
        sequences[directory] = frame_range
        extension = random.choice([".png", ".exr", ".tiff"])
        _random_missing_frames(directory, 0, frame_range, extension)

        # create incomplete sequences
        directory = os.path.join(base_dir, f"incomplete_sequences{i}")
        frame_range = (1001, 1150)
        sequences[directory] = frame_range
        extension = random.choice([".png", ".exr", ".tiff"])

        _random_missing_frames(directory, chance, frame_range, extension)

    return sequences


if __name__ == "__main__":
    base_dir = os.getcwd()
    base_dir = os.path.join(base_dir, "sample_data")
    logger = LoggerFactory.get_logger("main", os.path.join(os.getcwd(), "log"))

    # generate sample data
    logger.info(f"Generating Sample data in base_dir: {base_dir}")
    sequences = _generate_test_data(
        base_dir,
        10,
        20,
    )
    for key, value in sequences.items():
        logger.info(f"\t----- {str.replace(key, (base_dir + "\\"), "")}, frame-range: {value}")
    logger.info(f"Finished Generating Sample data.\n")

    # Parse Sequences
    logger.info(f"Parsing File Sequences:")
    complete = []
    incomplete = []
    for directory, frame_range in sequences.items():
        sequencer = FileSequenceParser(directory, frame_range)
        sequence_report = sequencer.generate_report()
        if sequence_report["status"] == "incomplete":
            incomplete.append(directory)
        else:
            complete.append(directory)
    logger.info(f"Finished Parsing File Sequences.")
    logger.info(f"{len(complete)} Complete Sequences: {complete}")
    logger.info(f"{len(incomplete)} Incomplete Sequences: {incomplete}")
