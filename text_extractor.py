import logging
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import re
from config_manager import get_setting
from search_replace_processor import apply_search_replace

def extract_text_from_html(html_content):
    """
    Extracts clean text from HTML content.

    Args:
        html_content (str): Raw HTML content.

    Returns:
        str: Cleaned text.
    """
    warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove script, style, and other unwanted tags
    for tag in soup(["script", "style", "meta", "link"]):
        tag.extract()

    # Extract text from paragraphs
    paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
    separator = '\n' if get_setting('preserve_paragraph_breaks') else ' '
    text = separator.join(paragraphs)

    # Normalize spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Handle line break removal based on config
    if get_setting('remove_line_breaks'):
        text = text.replace('\n', ' ')
        text = re.sub(r' +', ' ', text)
        logging.debug("Removed line breaks from extracted text")

    # Handle empty line removal
    if get_setting('remove_empty_lines'):
        if get_setting('preserve_paragraph_breaks'):
            text = re.sub(r'\n+', '\n', text)
        else:
            text = re.sub(r'\n+', '', text)
        logging.debug("Removed consecutive empty lines from extracted text")

    return text.strip()

def count_words(text):
    """
    Counts the number of words in the text.

    Args:
        text (str): Text to count words in.

    Returns:
        int: Word count.
    """
    return len(text.split())

def normalize_title_for_dedup(text):
    """
    Normalizes title text for deduplication by removing common prefixes.

    Args:
        text (str): Title text to normalize.

    Returns:
        str: Normalized title text.
    """
    text = text.strip()
    text = re.sub(r'^Chapter\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\d+:\s*', '', text)
    text = re.sub(r'^\d+\s*', '', text)
    return text.strip()

def extract_chapters_text(epub_processor, start_chapter, max_words, terms=None):
    """
    Extracts text from consecutive chapters starting from the given chapter,
    up to the maximum word count. Applies search-replace terms to each chapter if provided.

    Args:
        epub_processor (EpubProcessor): Instance of EpubProcessor.
        start_chapter (int): Starting chapter number (1-based).
        max_words (int): Maximum word count.
        terms (list, optional): List of search-replace term dictionaries.

    Returns:
        tuple: (extracted_text, included_chapters, total_words)
    """
    logging.info(f"Starting text extraction from chapter {epub_processor.get_real_chapter_number(start_chapter - 1)} with max words {max_words}")
    text = ""
    current_chapter = start_chapter
    total_words = 0
    included_chapters = []

    while total_words < max_words and current_chapter <= epub_processor.get_total_chapters():
        chapter_html = epub_processor.get_chapter_content(current_chapter)
        chapter_text = extract_text_from_html(chapter_html)
        if terms:
            chapter_text = apply_search_replace(chapter_text, terms)
        chapter_words = count_words(chapter_text)
        logging.debug(f"Processing chapter {current_chapter}, words in chapter: {chapter_words}")

        if total_words + chapter_words > max_words:
            # Don't include partial chapters
            logging.debug(f"Chapter {current_chapter} would exceed max words, stopping extraction")
            break

        if get_setting('include_chapter_titles'):
            chapter_title = epub_processor.get_chapter_title(current_chapter)
            if terms:
                chapter_title = apply_search_replace(chapter_title, terms)
            # Check for title duplication if enabled
            if get_setting('fix_title_duplication'):
                normalized_title = normalize_title_for_dedup(chapter_title)
                if normalized_title:
                    prefix_length = min(len(chapter_text), len(chapter_title) * 3 + 20)
                    normalized_text_start = normalize_title_for_dedup(chapter_text[:prefix_length])
                    if normalized_title.lower() in normalized_text_start.lower():
                        logging.debug(f"Skipped adding duplicate title '{chapter_title}' for chapter {current_chapter}")
                    else:
                        text += f"\n\n{chapter_title}\n\n"
                else:
                    text += f"\n\n{chapter_title}\n\n"
            else:
                text += f"\n\n{chapter_title}\n\n"

        text += chapter_text + "\n\n"
        total_words += chapter_words
        real_num = epub_processor.get_real_chapter_number(current_chapter - 1)
        included_chapters.append(real_num if real_num is not None else current_chapter)
        logging.info(f"Included chapter {real_num} with {chapter_words} words")
        current_chapter += 1

    logging.info(f"Extraction complete: included {len(included_chapters)} chapters, total words: {total_words}")
    return text.strip(), included_chapters, total_words