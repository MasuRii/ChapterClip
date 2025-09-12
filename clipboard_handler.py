import pyperclip
from utils.error_handler import ClipboardError

def copy_to_clipboard(text):
    """
    Copies the given text to the system clipboard.

    Args:
        text (str): Text to copy.

    Returns:
        bool: True if successful.

    Raises:
        ClipboardError: If copying fails.
    """
    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException as e:
        raise ClipboardError(f"Failed to copy to clipboard: {str(e)}")

def get_clipboard_content():
    """
    Retrieves content from the system clipboard.

    Returns:
        str: Clipboard content.

    Raises:
        ClipboardError: If accessing clipboard fails.
    """
    try:
        return pyperclip.paste()
    except pyperclip.PyperclipException as e:
        raise ClipboardError(f"Failed to access clipboard: {str(e)}")