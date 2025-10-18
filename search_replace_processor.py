import os
import json
import re
from utils.validators import validate_json_file, validate_search_replace_term
from utils.error_handler import SearchReplaceError
def fix_variable_lookbehind(pattern):
    """
    Fixes variable-width lookbehind patterns by refactoring them into fixed-width alternatives.

    Specifically handles patterns like "(?<=\\d|\\b)(cr)\\b" and converts them to
    "(?<=\\d)(cr)\\b|\\b(cr)\\b".

    Args:
        pattern (str): The regex pattern to fix.

    Returns:
        str: The fixed pattern, or the original if no fix is needed.
    """
    # Match lookbehind: (?<=content)
    lookbehind_match = re.search(r'\(\?<=([^)]*)\)', pattern)
    if not lookbehind_match:
        return pattern

    lb_content = lookbehind_match.group(1)
    if '|' not in lb_content:
        return pattern

    # Split alternatives
    alts = [alt.strip() for alt in lb_content.split('|')]

    # Get the part after the lookbehind
    lb_end = lookbehind_match.end()
    match_part = pattern[lb_end:]

    # Build new patterns
    new_patterns = []
    for alt in alts:
        if alt == '\\b':
            # For \b (zero-width), place it before the match
            new_pattern = f'\\b{match_part}'
        else:
            # For other alternatives, keep the lookbehind
            new_pattern = f'(?<={alt}){match_part}'
        new_patterns.append(new_pattern)

    return '|'.join(new_patterns)



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
        terms (list): List of term dictionaries with 'original', 'replacement', 'caseSensitive', 'isRegex', 'wholeWord'.

    Returns:
        str: The processed text with replacements applied.

    Raises:
        SearchReplaceError: If an error occurs during replacement.
    """
    try:
        # Categorize terms
        simple_cs_partial = {}
        simple_cs_whole = {}
        simple_ci_partial = {}
        simple_ci_whole = {}
        regex_terms = []
        for term in terms:
            orig = term['original']
            repl = term['replacement']
            cs = term['caseSensitive']
            is_rx = term['isRegex']
            whole = term.get('wholeWord', False)
            if is_rx:
                # Fix variable-width lookbehind patterns
                fixed_orig = fix_variable_lookbehind(orig)
                flags = 0 if cs else re.IGNORECASE
                regex_terms.append({'pattern': re.compile(fixed_orig, flags), 'replacement': repl})
            else:
                key = orig if cs else orig.lower()
                if cs:
                    if whole:
                        simple_cs_whole[key] = repl
                    else:
                        simple_cs_partial[key] = repl
                else:
                    if whole:
                        simple_ci_whole[key] = repl
                    else:
                        simple_ci_partial[key] = repl

        # Compile combined patterns
        compiled_terms = regex_terms.copy()
        def add_simple_group(map_dict, flags, whole_word, case_sensitive):
            if map_dict:
                sorted_keys = sorted(map_dict.keys(), key=len, reverse=True)
                patterns = []
                for k in sorted_keys:
                    escaped = re.escape(k)
                    if whole_word:
                        pattern = r'\b' + escaped + r'\b'
                    else:
                        pattern = escaped
                    patterns.append(pattern)
                combined = '|'.join(patterns)
                pattern = re.compile(combined, flags)
                compiled_terms.append({
                    'pattern': pattern,
                    'replacement_map': map_dict,
                    'is_simple': True,
                    'case_sensitive': case_sensitive
                })

        add_simple_group(simple_cs_partial, 0, False, True)
        add_simple_group(simple_cs_whole, 0, True, True)
        add_simple_group(simple_ci_partial, re.IGNORECASE, False, False)
        add_simple_group(simple_ci_whole, re.IGNORECASE, True, False)

        # Find all matches
        replacements = []
        for comp in compiled_terms:
            pat = comp['pattern']
            for match in pat.finditer(text):
                if match.start() == match.end():
                    continue
                matched_text = match.group(0)
                if comp.get('is_simple'):
                    key = matched_text if comp['case_sensitive'] else matched_text.lower()
                    repl = comp['replacement_map'].get(key)
                    if repl is not None:
                        replacements.append({'start': match.start(), 'end': match.end(), 'replacement': repl})
                else:
                    replacements.append({'start': match.start(), 'end': match.end(), 'replacement': comp['replacement']})

        # Sort: start asc, then end desc
        replacements.sort(key=lambda r: (r['start'], -r['end']))

        # Select non-overlapping
        winning = []
        last_end = -1
        for rep in replacements:
            if rep['start'] >= last_end:
                winning.append(rep)
                last_end = rep['end']

        # Sort by start desc
        winning.sort(key=lambda r: r['start'], reverse=True)

        # Apply
        result = text
        for rep in winning:
            start = rep['start']
            end = rep['end']
            repl = rep['replacement']
            result = result[:start] + repl + result[end:]

        return result

    except Exception as e:
        raise SearchReplaceError(f"Error applying search-replace: {str(e)}")