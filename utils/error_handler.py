import sys

class ChapterClipError(Exception):
    """Base exception for ChapterClip errors."""
    pass

class InvalidEpubError(ChapterClipError):
    """Raised when an invalid EPUB file is provided."""
    pass

class ChapterNotFoundError(ChapterClipError):
    """Raised when the specified chapter is not found in the EPUB."""
    pass

class ClipboardError(ChapterClipError):
    """Raised when clipboard operations fail."""
    pass

class ValidationError(ChapterClipError):
    """Raised when input validation fails."""
    pass

def handle_error(error, message=None, exit_code=1):
    """
    Handles errors gracefully by printing a message and optionally exiting.

    Args:
        error (Exception): The exception that occurred.
        message (str, optional): Custom error message.
        exit_code (int): Exit code for sys.exit (default 1).
    """
    if message:
        print(f"Error: {message}")
    else:
        print(f"Error: {str(error)}")

    if exit_code:
        sys.exit(exit_code)
    else:
        raise error

def safe_execute(func, *args, **kwargs):
    """
    Safely executes a function, catching and handling exceptions.

    Args:
        func (callable): The function to execute.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        The result of the function if successful.

    Raises:
        ChapterClipError: If an error occurs.
    """
    try:
        return func(*args, **kwargs)
    except ChapterClipError:
        raise
    except Exception as e:
        handle_error(e)