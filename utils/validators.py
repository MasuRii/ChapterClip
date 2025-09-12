import os
from .error_handler import ValidationError

def validate_epub_file(file_path):
    """
    Validates that the given file path is a valid EPUB file.

    Args:
        file_path (str): Path to the EPUB file.

    Raises:
        ValidationError: If the file does not exist or is not an EPUB.
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    if not file_path.lower().endswith('.epub'):
        raise ValidationError("File must be an EPUB file (.epub)")

def validate_chapter_number(chapter_num, max_chapters=None):
    """
    Validates the chapter number.

    Args:
        chapter_num: The chapter number to validate.
        max_chapters (int, optional): Maximum number of chapters available.

    Raises:
        ValidationError: If validation fails.
    """
    try:
        chapter_num = int(chapter_num)
    except ValueError:
        raise ValidationError("Chapter number must be an integer")

    if chapter_num < 1:
        raise ValidationError("Chapter number must be a positive integer")

    if max_chapters and chapter_num > max_chapters:
        raise ValidationError(f"Chapter number exceeds available chapters ({max_chapters})")

def validate_word_count(word_count):
    """
    Validates the word count setting.

    Args:
        word_count: The word count to validate.

    Raises:
        ValidationError: If validation fails.
    """
    try:
        word_count = int(word_count)
    except ValueError:
        raise ValidationError("Word count must be an integer")

    if word_count < 1:
        raise ValidationError("Word count must be a positive integer")

    if word_count > 100000:  # Arbitrary upper limit
        raise ValidationError("Word count cannot exceed 100,000")

def validate_yes_no_input(user_input):
    """
    Validates yes/no input.

    Args:
        user_input (str): User input.

    Returns:
        bool: True for 'y' or 'yes', False for 'n' or 'no'.

    Raises:
        ValidationError: If input is invalid.
    """
    user_input = user_input.lower().strip()
    if user_input in ['y', 'yes']:
        return True
    elif user_input in ['n', 'no']:
        return False
    else:
        raise ValidationError("Please enter 'y' or 'n'")