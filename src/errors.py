class SequenceError(Exception):
    """Base class for Sequence Related Errors"""

    pass


class InvalidFileNameError(Exception):
    """Base class for Invalid File Name Errors according to naming convention."""

    pass


class ProcessingError(Exception):
    """Base class for Processing Errors. (Currently simulating rendertime errors.)"""

    def __init__(self, message, job):
        super().__init__(message)
        self.job = job
