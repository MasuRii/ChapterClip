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
        "[2] Configure settings\n"
        "[3] View current settings\n"
        "[4] Exit\n",
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

def display_chapter_confirmation(chapter_num, title):
    """
    Displays chapter confirmation prompt.

    Args:
        chapter_num (int): Chapter number.
        title (str): Chapter title.

    Returns:
        bool: True if confirmed.
    """
    console.print(f"\n[bold]Chapter {chapter_num}: {title}[/bold]")
    confirmed = Confirm.ask("Is this the correct chapter?")
    return confirmed

def display_extraction_result(included_chapters, total_words, max_words):
    """
    Displays the extraction result summary.

    Args:
        included_chapters (list): List of included chapter numbers.
        total_words (int): Total words extracted.
        max_words (int): Maximum allowed words.
    """
    console.print("\n[bold green]Extraction Complete![/bold green]")
    console.print("✓ Successfully extracted and copied to clipboard\n")
    console.print("Details:")
    console.print(f"  • Chapters included: {included_chapters[0]}-{included_chapters[-1]} ({len(included_chapters)} chapters)")
    console.print(f"  • Total words: {total_words}")
    console.print(f"  • Maximum allowed: {max_words}")
    console.print("\nPress Enter to return to main menu...")
    input()

def display_settings():
    """
    Displays current settings in a table.
    """
    settings = load_config()['settings']
    table = Table(title="Current Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    for key, value in settings.items():
        table.add_row(key.replace('_', ' ').title(), str(value))
    console.print(table)

def configure_settings():
    """
    Allows user to configure settings.
    """
    console.print("\n[bold]Configure Settings[/bold]")
    console.print("1. Max words")
    console.print("2. Include chapter titles")
    console.print("3. Preserve paragraph breaks")
    console.print("4. Log level")
    choice = get_user_choice([1, 2, 3, 4])

    if choice == 1:
        current = get_setting('max_words')
        new_value = Prompt.ask(f"Enter new max words (current: {current})", default=str(current))
        try:
            new_value = int(new_value)
            set_setting('max_words', new_value)
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

    console.print("Press Enter to continue...")
    input()