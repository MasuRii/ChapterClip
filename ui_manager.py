from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from tkinter import filedialog
from tkinter import Tk
import os
from config_manager import get_setting, set_setting, load_config

console = Console()

def select_epub_file():
    """
    Opens a file dialog to select an EPUB file.

    Returns:
        str: Path to the selected EPUB file, or None if cancelled.
    """
    try:
        root = Tk()
        root.withdraw()  # Hide the main window
        initial_dir = get_setting('last_epub_directory') or os.getcwd()
        file_path = filedialog.askopenfilename(
            title="Select EPUB file",
            filetypes=[("EPUB files", "*.epub")],
            initialdir=initial_dir
        )
        root.destroy()
        if file_path:
            set_setting('last_epub_directory', os.path.dirname(file_path))
        return file_path
    except Exception:
        # Fallback to console input if GUI fails
        console.print("[yellow]GUI file picker failed, please enter file path manually:[/yellow]")
        return Prompt.ask("Enter EPUB file path")

def select_json_file():
    """
    Opens a file dialog to select a JSON file.

    Returns:
        str: Path to the selected JSON file, or None if cancelled.
    """
    try:
        root = Tk()
        root.withdraw()  # Hide the main window
        initial_dir = get_setting('last_json_directory') or os.getcwd()
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json")],
            initialdir=initial_dir
        )
        root.destroy()
        if file_path:
            set_setting('last_json_directory', os.path.dirname(file_path))
        return file_path
    except Exception:
        # Fallback to console input if GUI fails
        console.print("[yellow]GUI file picker failed, please enter file path manually:[/yellow]")
        return Prompt.ask("Enter JSON file path")

def display_main_menu():
    """
    Displays the main menu.
    """
    console.clear()
    panel = Panel.fit(
        "[bold blue]ChapterClip - EPUB Text Extractor[/bold blue]\n\n"
        "Please select an option:\n\n"
        "[1] Extract chapters from EPUB\n"
        "[2] Replace Epub Terms\n"
        "[3] Configure settings\n"
        "[4] View current settings\n"
        "[5] Exit\n",
        title="Main Menu"
    )
    console.print(panel)

def get_user_choice(options):
    """
    Gets user choice with validation.

    Args:
        options (list): List of valid choices.

    Returns:
        int: User's choice.
    """
    choice = Prompt.ask("Enter your choice", choices=[str(o) for o in options])
    return int(choice)

def display_chapter_confirmation(real_num, title):
    """
    Displays chapter confirmation prompt.

    Args:
        real_num (int): Real chapter number.
        title (str): Chapter title.

    Returns:
        bool: True if confirmed.
    """
    console.print(f"\n[bold]Chapter {real_num}: {title}[/bold]")
    confirmed = Confirm.ask("Is this the correct chapter?")
    return confirmed

def display_extraction_result(included_chapters, total_count, max_count):
    """
    Displays the extraction result summary.

    Args:
        included_chapters (list): List of included chapter numbers.
        total_count (int): Total count extracted (words or tokens).
        max_count (int): Maximum allowed count.
    """
    from config_manager import get_setting
    count_type = "tokens" if get_setting('counting_mode') == 'tokens' else "words"
    console.print("\n[bold green]Extraction Complete![/bold green]")
    console.print("✓ Successfully extracted and copied to clipboard\n")
    console.print("\nDetails:")
    console.print(f"  • Chapters included: {included_chapters[0]}-{included_chapters[-1]} ({len(included_chapters)} chapters)")
    console.print(f"  • Total {count_type}: {total_count}")
    console.print(f"  • Maximum allowed: {max_count}")

def display_post_extraction_menu():
    """
    Displays the post-extraction menu and gets user choice.

    Returns:
        int: User's choice (1, 2, or 3).
    """
    console.print("\nWhat would you like to do next?\n")
    console.print("[1] Recopy the extracted text to clipboard again")
    console.print("[2] Redo extraction with previous settings")
    console.print("[3] Return to the main menu")
    choice = get_user_choice([1, 2, 3])
    return choice
def display_replacement_result(processed_items, output_path):
    """
    Displays the replacement result summary.

    Args:
        processed_items (int): Number of items processed.
        output_path (str): Path to the output EPUB file.
    """
    console.print("\n[bold green]Term Replacement Complete![/bold green]")
    console.print("✓ Successfully processed EPUB with term replacements\n")
    console.print("\nDetails:")
    console.print(f"  • HTML items processed: {processed_items}")
    console.print(f"  • Output file: {output_path}")

def display_replacement_confirmation(terms_count, epub_path):
    """
    Displays confirmation for term replacement operation.

    Args:
        terms_count (int): Number of terms loaded.
        epub_path (str): Path to the EPUB file.

    Returns:
        bool: True if confirmed.
    """
    from rich.prompt import Confirm
    console.print(f"\n[bold]Ready to process EPUB:[/bold] {epub_path}")
    console.print(f"[bold]Terms loaded:[/bold] {terms_count}")
    confirmed = Confirm.ask("Proceed with term replacement?")
    return confirmed

def display_settings():
    """
    Displays current settings in tables for general and performance settings.
    """
    settings = load_config()['settings']

    # Performance settings keys
    performance_keys = ['enable_parallel_processing', 'max_workers', 'enable_content_filtering', 'min_word_count_threshold', 'exclusion_keywords']

    # General settings table
    general_table = Table(title="General Settings")
    general_table.add_column("Setting", style="cyan")
    general_table.add_column("Value", style="magenta")

    # Performance settings table
    performance_table = Table(title="Performance Settings")
    performance_table.add_column("Setting", style="cyan")
    performance_table.add_column("Value", style="magenta")

    for key, value in settings.items():
        if key in performance_keys:
            # Format performance settings with clear labels
            if key == 'enable_parallel_processing':
                display_value = "Enabled" if value else "Disabled"
                label = "Parallel Processing"
            elif key == 'max_workers':
                display_value = str(value)
                label = "Max Workers"
            elif key == 'enable_content_filtering':
                display_value = "Enabled" if value else "Disabled"
                label = "Content Filtering"
            elif key == 'min_word_count_threshold':
                display_value = str(value)
                label = "Min Word Count Threshold"
            elif key == 'exclusion_keywords':
                display_value = ', '.join(value) if isinstance(value, list) else str(value)
                label = "Exclusion Keywords"
            else:
                label = key.replace('_', ' ').title()
                display_value = str(value)
            performance_table.add_row(label, display_value)
        elif key not in ['last_extraction_params', 'last_epub_directory', 'last_json_directory']:
            # Exclude internal/directory settings from general table
            general_table.add_row(key.replace('_', ' ').title(), str(value))

    console.print(general_table)
    console.print()  # Add space between tables
    console.print(performance_table)

def configure_settings():
    """
    Allows user to configure settings.
    """
    counting_mode = get_setting('counting_mode')
    label = "Max tokens" if counting_mode == 'tokens' else "Max words"
    console.print("\n[bold]Configure Settings[/bold]")
    console.print(f"1. {label}")
    console.print("2. Include chapter titles")
    console.print("3. Preserve paragraph breaks")
    console.print("4. Log level")
    console.print("5. Remove line breaks")
    console.print("6. Remove empty lines")
    console.print("7. Fix title duplication")
    console.print("8. Counting mode")
    console.print("9. Enable parallel processing")
    console.print("10. Max workers")
    console.print("11. Enable content filtering")
    console.print("12. Min word count threshold")
    console.print("13. Manage exclusion keywords")
    choice = get_user_choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

    if choice == 1:
        key = 'max_tokens' if counting_mode == 'tokens' else 'max_words'
        current = get_setting(key)
        count_type = 'tokens' if counting_mode == 'tokens' else 'words'
        new_value = Prompt.ask(f"Enter new max {count_type} (current: {current})", default=str(current))
        try:
            new_value = int(new_value)
            set_setting(key, new_value)
            console.print("[green]Setting updated![/green]")
        except ValueError:
            console.print("[red]Invalid value![/red]")
    elif choice == 2:
        current = get_setting('include_chapter_titles')
        new_value = Confirm.ask(f"Include chapter titles? (current: {current})", default=current)
        set_setting('include_chapter_titles', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 3:
        current = get_setting('preserve_paragraph_breaks')
        new_value = Confirm.ask(f"Preserve paragraph breaks? (current: {current})", default=current)
        set_setting('preserve_paragraph_breaks', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 4:
        current = get_setting('log_level')
        new_value = Prompt.ask(f"Select log level (current: {current})", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default=current)
        set_setting('log_level', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 5:
        current = get_setting('remove_line_breaks')
        new_value = Confirm.ask(f"Remove line breaks? (current: {current})", default=current)
        set_setting('remove_line_breaks', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 6:
        current = get_setting('remove_empty_lines')
        new_value = Confirm.ask(f"Remove empty lines? (current: {current})", default=current)
        set_setting('remove_empty_lines', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 7:
        current = get_setting('fix_title_duplication')
        new_value = Confirm.ask(f"Fix title duplication? (current: {current})", default=current)
        set_setting('fix_title_duplication', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 8:
        current = get_setting('counting_mode')
        new_value = Prompt.ask(f"Select counting mode (current: {current})", choices=['words', 'tokens'], default=current)
        set_setting('counting_mode', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 9:
        current = get_setting('enable_parallel_processing')
        new_value = Confirm.ask(f"Enable parallel processing? (current: {current})", default=current)
        set_setting('enable_parallel_processing', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 10:
        current = get_setting('max_workers')
        new_value = Prompt.ask(f"Enter max workers (current: {current})", default=str(current))
        try:
            new_value = int(new_value)
            if new_value > 0:
                set_setting('max_workers', new_value)
                console.print("[green]Setting updated![/green]")
            else:
                console.print("[red]Max workers must be greater than 0![/red]")
        except ValueError:
            console.print("[red]Invalid value! Must be a number.[/red]")
    elif choice == 11:
        current = get_setting('enable_content_filtering')
        new_value = Confirm.ask(f"Enable content filtering? (current: {current})", default=current)
        set_setting('enable_content_filtering', new_value)
        console.print("[green]Setting updated![/green]")
    elif choice == 12:
        current = get_setting('min_word_count_threshold')
        new_value = Prompt.ask(f"Enter min word count threshold (current: {current})", default=str(current))
        try:
            new_value = int(new_value)
            if new_value >= 0:
                set_setting('min_word_count_threshold', new_value)
                console.print("[green]Setting updated![/green]")
            else:
                console.print("[red]Min word count threshold must be 0 or greater![/red]")
        except ValueError:
            console.print("[red]Invalid value! Must be a number.[/red]")
    elif choice == 13:
        current_keywords = get_setting('exclusion_keywords')
        console.print(f"Current exclusion keywords: {', '.join(current_keywords)}")
        action = Prompt.ask("Choose action", choices=['add', 'remove', 'replace'], default='add')
        if action == 'add':
            new_keyword = Prompt.ask("Enter keyword to add")
            if new_keyword and new_keyword not in current_keywords:
                current_keywords.append(new_keyword)
                set_setting('exclusion_keywords', current_keywords)
                console.print("[green]Keyword added![/green]")
            else:
                console.print("[yellow]Keyword already exists or is empty.[/yellow]")
        elif action == 'remove':
            if current_keywords:
                remove_keyword = Prompt.ask("Enter keyword to remove", choices=current_keywords)
                current_keywords.remove(remove_keyword)
                set_setting('exclusion_keywords', current_keywords)
                console.print("[green]Keyword removed![/green]")
            else:
                console.print("[yellow]No keywords to remove.[/yellow]")
        elif action == 'replace':
            console.print("Enter new keywords separated by commas:")
            new_keywords_input = Prompt.ask("New keywords")
            new_keywords = [kw.strip() for kw in new_keywords_input.split(',') if kw.strip()]
            if new_keywords:
                set_setting('exclusion_keywords', new_keywords)
                console.print("[green]Keywords replaced![/green]")
            else:
                console.print("[yellow]No valid keywords entered.[/yellow]")

    console.print("Press Enter to continue...")
    input()