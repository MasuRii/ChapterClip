import os
import yaml
from utils.error_handler import handle_error

CONFIG_FILE = 'config.yaml'

DEFAULT_CONFIG = {
    'settings': {
        'max_words': 20000,
        'max_tokens': 20000,
        'include_chapter_titles': True,
        'log_level': 'INFO',
        'preserve_paragraph_breaks': True,
        'last_epub_directory': '',
        'last_json_directory': '',
        'remove_line_breaks': False,
        'remove_empty_lines': False,
        'fix_title_duplication': True,
        'counting_mode': 'words',
        'last_extraction_params': None
    }
}

def load_config():
    """
    Loads the configuration from the config file.
    If the file doesn't exist, creates it with default values.

    Returns:
        dict: Configuration dictionary.
    """
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config is None:
                config = DEFAULT_CONFIG
            # Merge with defaults
            for key, value in DEFAULT_CONFIG['settings'].items():
                if key not in config.get('settings', {}):
                    config['settings'][key] = value
            # Validate configuration
            validate_config(config)
            return config
    except Exception as e:
        handle_error(e, "Failed to load configuration")

def save_config(config):
    """
    Saves the configuration to the config file.

    Args:
        config (dict): Configuration dictionary to save.
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
        handle_error(e, "Failed to save configuration")

def validate_config(config):
    """
    Validates the configuration settings.
    Corrects invalid values to defaults.

    Args:
        config (dict): Configuration dictionary to validate.
    """
    boolean_keys = ['remove_line_breaks', 'remove_empty_lines', 'fix_title_duplication']
    for key in boolean_keys:
        if key in config.get('settings', {}):
            if not isinstance(config['settings'][key], bool):
                print(f"Warning: Invalid value for '{key}' in config. Expected boolean, using default: {DEFAULT_CONFIG['settings'][key]}")
                config['settings'][key] = DEFAULT_CONFIG['settings'][key]

    # Validate counting_mode
    if 'counting_mode' in config.get('settings', {}):
        if config['settings']['counting_mode'] not in ['words', 'tokens']:
            print(f"Warning: Invalid value for 'counting_mode' in config. Expected 'words' or 'tokens', using default: {DEFAULT_CONFIG['settings']['counting_mode']}")
            config['settings']['counting_mode'] = DEFAULT_CONFIG['settings']['counting_mode']

def get_setting(key):
    """
    Retrieves a setting value.

    Args:
        key (str): Setting key.

    Returns:
        Value of the setting.
    """
    config = load_config()
    return config['settings'].get(key)
def get_last_extraction_params():
    """
    Retrieves the last extraction parameters.

    Returns:
        dict or None: Last extraction parameters, or None if not set.
    """
    config = load_config()
    return config['settings'].get('last_extraction_params')

def save_last_extraction_params(params):
    """
    Saves the last extraction parameters.

    Args:
        params (dict or None): Extraction parameters to save, or None to clear.
    """
    config = load_config()
    config['settings']['last_extraction_params'] = params
    save_config(config)

def set_setting(key, value):
    """
    Sets a setting value and saves the config.

    Args:
        key (str): Setting key.
        value: Setting value.
    """
    config = load_config()
    config['settings'][key] = value
    save_config(config)