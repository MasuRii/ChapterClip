import json
import re
from utils.validators import validate_json_file, validate_search_replace_term
from utils.error_handler import SearchReplaceError


def load_search_replace_terms(file_path):
    """
    Loads and validates search-replace terms from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing an array of term objects.

    Returns:
        list: List of validated term dictionaries.

    Raises:
        SearchReplaceError: If loading or validation fails.
    """
    try:
        validate_json_file(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            terms = json.load(f)

        if not isinstance(terms, list):
            raise SearchReplaceError("JSON file must contain an array of term objects.")

        validated_terms = []
        for term in terms:
            validated_term = validate_search_replace_term(term)
            validated_terms.append(validated_term)

        return validated_terms

    except json.JSONDecodeError as e:
        raise SearchReplaceError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise SearchReplaceError(f"Error loading search-replace terms: {str(e)}")


def apply_search_replace(text, terms):
    """
    Applies search-replace terms to the given text sequentially.

    Args:
        text (str): The original text to process.
        terms (list): List of term dictionaries with 'original', 'replacement', 'caseSensitive', 'isRegex'.

    Returns:
        str: The processed text with replacements applied.

    Raises:
        SearchReplaceError: If an error occurs during replacement.
    """
    try:
        for term in terms:
            original = term['original']
            replacement = term['replacement']
            case_sensitive = term['caseSensitive']
            is_regex = term['isRegex']

            flags = 0 if case_sensitive else re.IGNORECASE

            if is_regex:
                pattern = original
            else:
                pattern = re.escape(original)

            text = re.sub(pattern, replacement, text, flags=flags)

        return text

    except Exception as e:
        raise SearchReplaceError(f"Error applying search-replace: {str(e)}")