import click
import logging
from rich.console import Console
from rich.prompt import Prompt
from ui_manager import (
    display_main_menu, get_user_choice, display_chapter_confirmation,
    display_extraction_result, display_settings, configure_settings, select_epub_file, select_json_file
)
from epub_processor import EpubProcessor
from text_extractor import extract_chapters_text, count_words
from clipboard_handler import copy_to_clipboard
from utils.validators import validate_epub_file, validate_chapter_number, validate_yes_no_input
from utils.error_handler import handle_error, SearchReplaceError
from search_replace_processor import load_search_replace_terms, apply_search_replace
from config_manager import get_setting

console = Console()

@click.group()
def cli():
    """ChapterClip - EPUB Text Extractor"""
    pass

@cli.command()
def run():
    """Run the interactive ChapterClip application."""
    log_level_name = get_setting('log_level')
    logging.basicConfig(level=logging.getLevelName(log_level_name), format='%(levelname)s: %(message)s')
    logging.info("ChapterClip application started.")
    while True:
        display_main_menu()
        choice = get_user_choice([1, 2, 3, 4])
        logging.debug(f"Menu choice: {choice}")
        if choice == 1:
            handle_extraction()
        elif choice == 2:
            configure_settings()
        elif choice == 3:
            display_settings()
            Prompt.ask("Press Enter to continue")
        elif choice == 4:
            logging.info("ChapterClip application exiting.")
            console.print("[bold blue]Goodbye![/bold blue]")
            break

def handle_extraction():
    """Handles the chapter extraction workflow."""
    file_path = select_epub_file()
    if not file_path:
        logging.debug("No EPUB file selected.")
        return

    try:
        logging.debug(f"Selected file: {file_path}")
        validate_epub_file(file_path)
        processor = EpubProcessor(file_path)
        max_chapters = processor.get_total_chapters()
        logging.info(f"Loaded EPUB with {max_chapters} chapters.")

        if max_chapters == 0:
            console.print("[red]No chapters found in the EPUB file.[/red]")
            Prompt.ask("Press Enter to continue")
            return

        chapter_input = Prompt.ask(f"Enter the chapter number (1-{max_chapters})")
        try:
            chapter_num = int(chapter_input)
        except ValueError:
            console.print("[red]Invalid chapter number.[/red]")
            Prompt.ask("Press Enter to continue")
            return

        validate_chapter_number(chapter_num, max_chapters)
        title = processor.get_chapter_title(chapter_num)
        logging.debug(f"Selected chapter {chapter_num}: {title}")

        if not display_chapter_confirmation(chapter_num, title):
            logging.debug("Chapter confirmation declined.")
            return

        max_words = get_setting('max_words')
        text, included_chapters, total_words = extract_chapters_text(processor, chapter_num, max_words)
        logging.info(f"Extracted text from chapters {included_chapters[0]}-{included_chapters[-1]}, total words: {total_words}")

        if not text:
            logging.warning("No text extracted. The chapter might be empty or exceed word limits.")
            console.print("[yellow]No text extracted. The chapter might be empty or exceed word limits.[/yellow]")
            Prompt.ask("Press Enter to continue")
            return

        # Optional search-replace feature
        use_search_replace = Prompt.ask("Do you have a JSON file with search-replace terms? (y/n)")
        try:
            use_sr = validate_yes_no_input(use_search_replace)
        except ValueError:
            console.print("[red]Invalid input. Skipping search-replace.[/red]")
            use_sr = False

        if use_sr:
            while True:
                json_path = select_json_file()
                try:
                    terms = load_search_replace_terms(json_path)
                    text = apply_search_replace(text, terms)
                    # Recalculate word count after search-replace processing
                    total_words = count_words(text)
                    logging.info(f"Word count after search-replace: {total_words}")
                    console.print("[green]Search-replace applied successfully.[/green]")
                    break
                except (SearchReplaceError, Exception) as e:
                    console.print(f"[red]Error processing search-replace: {str(e)}[/red]")
                    retry = Prompt.ask("Would you like to retry with a different file or skip? (retry/skip)")
                    if retry.lower().strip() not in ['retry', 'r']:
                        console.print("[yellow]Skipping search-replace.[/yellow]")
                        break

        copy_to_clipboard(text)
        display_extraction_result(included_chapters, total_words, max_words)

    except Exception as e:
        logging.error(f"Error during extraction: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        Prompt.ask("Press Enter to continue")

if __name__ == '__main__':
    cli()