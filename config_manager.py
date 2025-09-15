import os
import yaml
from utils.error_handler import handle_error

CONFIG_FILE = 'config.yaml'

DEFAULT_CONFIG = {
    'settings': {
        'max_words': 20000,
        'include_chapter_titles': True,
        'log_level': 'INFO',
        'preserve_paragraph_breaks': True,
        'last_epub_directory': '',
        'last_json_directory': ''
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