from typing import Optional

class YetundeError(Exception):
    """Base exception class for yetunde package.

    Attributes:
        url (str): The URL that caused the error.
        error_type (str): The type of error ('download' or 'extraction').
        original_error (Exception, optional): The original exception raised by yt-dlp.
        message (str): A descriptive error message.
    """

    def __init__(
        self,
        message: str,
        url: str,
        error_type: str,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.url = url
        self.error_type = error_type
        self.original_error = original_error

    def __str__(self):
        return f"[{self.error_type.upper()} ERROR] {self.message} (URL: {self.url})"
