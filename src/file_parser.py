import os
import re
from typing import Optional, Tuple, List, Dict

from src.errors import InvalidFileNameError, SequenceError
from src.logger import LoggerFactory

_logger = LoggerFactory.get_logger("FileSequenceParser", os.path.join(os.getcwd(), "log"))


class File:
    """The File Class adds functionality for reading naming conventions of files as well as sorting functionality."""

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

    def __init__(self, file_name, directory, naming_convention: Optional[str] = None):
        self.file_name = file_name
        self.directory = directory
        self.components = {}
        self.naming_convention = naming_convention or self.DEFAULT_NAMING_CONVENTION
        self._parse_filename()

    # ---- Naming Convention Functionality

    def _build_pattern(self):
        """Build regex pattern from tokens according to a naming_convention."""
        pattern = self.naming_convention  # store template
        for token, regex in self.TOKENS.items():
            pattern = pattern.replace(f"<{token}>", regex)  # replace each token with its given regex
        pattern = f"{pattern}$"

        return re.compile(pattern)

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

    def __repr__(self):
        """Represent this class as a string."""
        return self.file_name

    def __lt__(self, other):
        """
        Define when a file is less than another file. Currently it sorts by frame number.
        Could be extended in the future to include, AOVs, users, versions etc.
        """

        return int(self.components.get("frame", 0)) < int(other.components.get("frame", 0))


class FileSequenceParser:
    """Class for parsing a sequence file directory and detecting missing frames."""

    def __init__(self, directory: str, frame_range: Optional[Tuple[int, int]] = None):
        self.directory = directory
        self.frame_range = frame_range or None
        self.sequence, self.invalid_files = self.read_directory()

    def read_directory(self) -> Tuple[List[File], List[File]]:
        """
        Read the directory and parse the sequence.
        It will list invalid files, such as for example a tmp or README.txt
        """

        sequence = []
        invalid_files = []

        try:
            for root, dirs, files in os.walk(self.directory):
                for file in files:

                    # check for naming_convention
                    try:
                        new_file = File(file, self.directory)
                        sequence.append(new_file)
                    except InvalidFileNameError:
                        invalid_files.append(file)
                        _logger.warning(f"Invalid file name: {file} in directory: {self.directory}")
                sequence = sorted(sequence)
                return sequence, invalid_files
        except OSError as e:
            raise RuntimeError(f"Error while parsing directory: {self.directory}") from e

        return [], []

    def check_missing_frames(self) -> List[int]:
        """Validates the frame sequence of the directory for file sequences of the valid formats.
        Takes an optional frame_range to check if the first and last frame exists."""

        missing_frames = []

        # check if sequence exists
        if not self.sequence:
            if self.frame_range:
                missing_frames = list(range(self.frame_range[0], self.frame_range[1] + 1))
                return missing_frames
            else:
                raise SequenceError(f"No sequence found in directory: {self.directory}")
        else:
            # case: sequence exists, so check for missing frames
            sequence_frames = list(sorted([int(f.components.get("frame", 0)) for f in self.sequence]))
            if self.frame_range:
                frames_expected = list(range(self.frame_range[0], self.frame_range[1] + 1))
            else:
                frames_expected = list(range(sequence_frames[0], sequence_frames[-1] + 1))
            missing_frames = [frame for frame in frames_expected if frame not in sequence_frames]
            return missing_frames

    def get_sequence(self) -> List[File]:
        """Return the sequence of the files in the directory."""

        return self.sequence

    def generate_report(self) -> Dict[str, List[File]]:
        """
        Generates a report of the file sequences formated as:
        summary: sequence status: complete / incomplete :  xxxx/xxxx frames are missing
        missing_frames : list of missing frames
        """
        report = {}
        try:
            missing_frames = self.check_missing_frames()
        except SequenceError:
            _logger.error(f"Could not find missing_frames for sequence in directory: {self.directory}")

        if len(missing_frames) > 0:
            report["status"] = "incomplete"
            report["summary"] = f"Sequence incomplete : {len(missing_frames)} frames missing"
        if len(missing_frames) == 0:
            report["status"] = "complete"
            report["summary"] = f"Sequence complete : {len(missing_frames)} frames missing"

        report["missing_frames"] = missing_frames
        return report
