import os
import json
import re
from utils.validators import validate_json_file, validate_search_replace_term
from utils.error_handler import SearchReplaceError


def load_search_replace_terms(file_path, epub_path=None):
    """
    Loads and validates search-replace terms from a JSON file.

    Supports both old format (direct array of term objects) and new nested object format.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        list: List of validated term dictionaries.

    Raises:
        SearchReplaceError: If loading or validation fails.
    """
    try:
        validate_json_file(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            # Old format
            terms = data
        elif isinstance(data, dict):
            # New format
            if not all(key in data for key in ['formatVersion', 'settings', 'terms']):
                raise SearchReplaceError("New format JSON must contain 'formatVersion', 'settings', and 'terms'.")
            if epub_path:
                game_name = os.path.basename(epub_path).replace('.epub', '').lower().replace('_', '-')
            else:
                game_name = os.path.basename(file_path).replace('-terms.json', '')
            if game_name not in data['terms']:
                raise SearchReplaceError(f"No terms found for game '{game_name}'.")
            if data['settings'].get(game_name, {}).get('isDisabled', False):
                raise SearchReplaceError(f"Game '{game_name}' is disabled.")
            terms = data['terms'][game_name]
            if not isinstance(terms, list):
                raise SearchReplaceError(f"Terms for game '{game_name}' must be an array.")
        else:
            raise SearchReplaceError("JSON must be an array (old format) or object (new format).")

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
    Applies search-replace terms to the given text using batched replacement to handle overlaps and prioritization.

    Args:
        text (str): The original text to process.
        terms (list): List of term dictionaries with 'original', 'replacement', 'caseSensitive', 'isRegex'.

    Returns:
        str: The processed text with replacements applied.

    Raises:
        SearchReplaceError: If an error occurs during replacement.
    """
    try:
        # Separate terms into regex and non-regex groups
        regex_terms = []
        simple_cs = {}
        simple_ci = {}
        for term in terms:
            orig = term['original']
            repl = term['replacement']
            cs = term['caseSensitive']
            is_rx = term['isRegex']
            if is_rx:
                flags = 0 if cs else re.IGNORECASE
                pattern = re.compile(orig, flags)
                regex_terms.append({'pattern': pattern, 'replacement': repl})
            else:
                if cs:
                    simple_cs[orig] = repl
                else:
                    simple_ci[orig.lower()] = repl

        # Compile combined patterns for non-regex terms
        compiled_terms = regex_terms.copy()
        if simple_cs:
            sorted_keys_cs = sorted(simple_cs.keys(), key=len, reverse=True)
            combined_cs = '|'.join(re.escape(k) for k in sorted_keys_cs)
            pattern_cs = re.compile(combined_cs)
            compiled_terms.append({'pattern': pattern_cs, 'replacement_map': simple_cs, 'is_simple': True, 'case_sensitive': True})
        if simple_ci:
            sorted_keys_ci = sorted(simple_ci.keys(), key=len, reverse=True)
            combined_ci = '|'.join(re.escape(k) for k in sorted_keys_ci)
            pattern_ci = re.compile(combined_ci, re.IGNORECASE)
            compiled_terms.append({'pattern': pattern_ci, 'replacement_map': simple_ci, 'is_simple': True, 'case_sensitive': False})

        # Find all matches
        replacements = []
        for comp in compiled_terms:
            pat = comp['pattern']
            for match in pat.finditer(text):
                if match.start() == match.end():
                    continue  # Skip zero-length matches
                matched_text = match.group(0)
                if comp.get('is_simple'):
                    key = matched_text if comp['case_sensitive'] else matched_text.lower()
                    repl = comp['replacement_map'].get(key)
                    if repl is not None:
                        replacements.append({'start': match.start(), 'end': match.end(), 'replacement': repl})
                else:
                    replacements.append({'start': match.start(), 'end': match.end(), 'replacement': comp['replacement']})

        # Sort matches by start position ascending, then by match length descending
        replacements.sort(key=lambda r: (r['start'], -(r['end'] - r['start'])))

        # Select non-overlapping replacements
        winning = []
        last_end = -1
        for rep in replacements:
            if rep['start'] >= last_end:
                winning.append(rep)
                last_end = rep['end']

        # Sort winning replacements by start position descending for reverse order application
        winning.sort(key=lambda r: r['start'], reverse=True)

        # Apply replacements in reverse order
        result = text
        for rep in winning:
            start = rep['start']
            end = rep['end']
            repl = rep['replacement']
            result = result[:start] + repl + result[end:]

        return result

    except Exception as e:
        raise SearchReplaceError(f"Error applying search-replace: {str(e)}")