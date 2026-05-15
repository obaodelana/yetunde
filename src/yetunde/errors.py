class YetundeError(Exception):
    """Base exception class for yetunde package."""
    pass

class DownloadError(YetundeError):
    """Exception raised for errors during download."""
    pass

class ExtractionError(YetundeError):
    """Exception raised for errors extracting info from URL."""
    pass
