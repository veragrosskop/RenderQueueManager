import os
import re
from typing import Optional, Tuple, List, Dict
from collections import defaultdict

from src.constants import LOGS_DIR
from src.errors import InvalidFileNameError, SequenceError
from src.logger import LoggerFactory

_logger = LoggerFactory.get_logger("FileSequenceParser", LOGS_DIR)


class File:
    """
    Wrapper around a tokenized file representation for parsing e.g. frame numbers, extensions etc. Parses all data
    on initialization.
    """

    # supported file extensions
    VALID_EXTENSIONS = ["png", "jpg", "tiff", "exr"]

    # naming conventions (flexibly add more later if wanted)
    DEFAULT_NAMING_CONVENTION = "<name>_<frame>.<ext>"

    # regex tokens for naming conventions
    TOKENS = {
        "name": r"(?P<name>[a-zA-Z0-9]+)",  # name regex group: any number of letters and numbers
        # "version": r"(?P<version>v\d{3})",    #versions for future implementation
        # "user": r"(?P<user>[a-zA-Z]+)",       #user for future implementation
        "frame": r"(?P<frame>\d{4})",  # frame regex group: exactly 4 digits
        "ext": r"(?P<ext>{})".format("|".join(VALID_EXTENSIONS)),  # ext regex group: one of the valid extensions
    }

    def __init__(
        self,
        file_name: str,
        directory: str,
        naming_convention: Optional[str] = None,
    ):
        self.file_name = file_name
        self.directory = directory
        self.components = {}
        self.naming_convention = naming_convention or self.DEFAULT_NAMING_CONVENTION
        self._parse_filename()

    # ---- Naming Convention Functionality

    def _parse_filename(self):
        """Parse the file name and extract components based on the naming_convention."""

        pattern = self._build_pattern()
        match = pattern.fullmatch(self.file_name)
        if match:
            self.components = match.groupdict()
        else:
            raise InvalidFileNameError(
                f"Filename '{self.file_name}' does not match naming convention: {self.naming_convention}"
            )

    def _build_pattern(self):
        """Build regex pattern from tokens according to a naming_convention."""

        pattern = self.naming_convention
        for token, regex in self.TOKENS.items():
            pattern = pattern.replace(f"<{token}>", regex)  # replace each token with its given regex
        pattern = f"{pattern}$"

        return re.compile(pattern)

    def __repr__(self):
        return self.file_name

    def __lt__(self, other: "File"):
        """
        Define when a file is less than another file. Currently, it sorts by frame number.
        Could be extended in the future to include, AOVs, users, versions etc.
        """

        return int(self.components.get("frame", 0)) < int(other.components.get("frame", 0))


class FileSequenceParser:
    """
    Class for parsing a sequence file directory and detecting missing frames.

    Supports multiple sequences in a single directory, splitting these by the <name> token on the files' grammar.
    """

    def __init__(self, directory: str, frame_range: Optional[Tuple[int, int]] = None):
        self.directory = directory
        self.frame_range = frame_range or None

        result = self.read_directory()
        self.sequences: Dict[str, List[File]] = result[0]
        self.invalid_files: List[File] = result[1]

    def read_directory(self) -> Tuple[Dict[str, File], List[File]]:
        """
        Read the directory and parse the sequence.
        It will list invalid files, such as for example a tmp or README.txt
        """

        sequences: Dict[str, List[File]] = defaultdict(list)
        invalid_files = []

        try:
            for _, _, files in os.walk(self.directory):
                for file in files:

                    # check for naming_convention
                    try:
                        new_file = File(file, self.directory)
                        sequences[new_file.components["name"]].append(new_file)
                    except InvalidFileNameError:
                        invalid_files.append(file)
                        _logger.warning(f"Invalid file name: {file} in directory: {self.directory}")

                sequences = {name: sorted(sequence) for name, sequence in sequences.items()}

                # Don't recurse into subfolders, only consider top level files.
                return sequences, invalid_files
        except OSError as e:
            raise RuntimeError(f"Error while parsing directory: {self.directory}") from e

        return {}, []

    def check_missing_frames_in_sequence(self, sequence: List[File]) -> List[int]:
        """Checks if a single sequence is missing frames and returns those frame numbers."""

        sequence_frames = list(sorted([int(f.components.get("frame", 0)) for f in sequence]))
        if self.frame_range:
            frames_expected = list(range(self.frame_range[0], self.frame_range[1] + 1))
        else:
            frames_expected = list(range(sequence_frames[0], sequence_frames[-1] + 1))
        missing_frames = [frame for frame in frames_expected if frame not in sequence_frames]
        return missing_frames

    def check_missing_frames(self) -> Dict[str, List[int]]:
        """
        Validates the frame sequence of the directory for file sequences of the valid formats.
        """

        missing_frames: Dict[str, List[int]] = {}

        if not self.sequences:
            raise SequenceError(f"No sequence found in directory: {self.directory}")

        for name, sequence in self.sequences.items():
            # check if sequence exists
            if not sequence:
                if self.frame_range:
                    missing_frames[name] = list(range(self.frame_range[0], self.frame_range[1] + 1))
                else:
                    raise SequenceError(f"No sequence found in directory: {self.directory}")
            else:
                missing_frames[name] = self.check_missing_frames_in_sequence(sequence)

        return missing_frames

    def generate_report(self) -> Dict[str, Dict[str, List[File]]]:
        """
        Generates a report of the file sequences formated as:
        name:
            status: 'complete' or 'incomplete'
            summary: sequence status: complete / incomplete :  x frames missing
            missing_frames : list of missing frame numbers
        """
        report = {}
        try:
            missing_frames = self.check_missing_frames()
        except SequenceError:
            _logger.error(f"Could not find missing_frames for sequence in directory: {self.directory}")

        for name, sequence in self.sequences.items():

            subreport = {}

            if len(missing_frames[name]) > 0:
                subreport["status"] = "incomplete"
                subreport["summary"] = f"Sequence incomplete : {len(missing_frames[name])} frames missing"
            if len(missing_frames[name]) == 0:
                subreport["status"] = "complete"
                subreport["summary"] = f"Sequence complete : {len(missing_frames[name])} frames missing"

            subreport["missing_frames"] = missing_frames[name]

            report[name] = subreport

        return report
