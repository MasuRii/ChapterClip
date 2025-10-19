import logging
import re
import os
import concurrent.futures
from ebooklib import epub
from utils.error_handler import InvalidEpubError, ChapterNotFoundError
from config_manager import get_setting

class EpubProcessor:
    """
    Handles EPUB file processing, including loading and extracting chapters.
    """

    def __init__(self, file_path):
        """
        Initializes the EpubProcessor with the given file path.

        Args:
            file_path (str): Path to the EPUB file.
        """
        self.file_path = file_path
        self.book = None
        self.chapters = []
        self.real_chapter_numbers = []
        self.real_to_index = {}
        self.load_book()

    def load_book(self):
        """
        Loads the EPUB book and extracts chapters.
        """
        try:
            self.book = epub.read_epub(self.file_path)
            self.chapters = self.get_chapters()
            # Populate real chapter numbers
            for idx, item in enumerate(self.chapters):
                num, method, source = self.extract_chapter_number(item)
                self.real_chapter_numbers.append(num)
                logging.debug(f"Chapter index {idx}: source='{source}', extracted={num}, method={method}")
                if num is not None:
                    self.real_to_index[num] = idx
                    logging.debug(f"Chapter index {idx}: real number {num}, filename {item.get_name()}")
                else:
                    logging.info(f"Chapter index {idx}: no real number extracted, filename {item.get_name()}")
            logging.debug(f"Real to index mapping: {self.real_to_index}")
            logging.info(f"Loaded EPUB file: {self.file_path}")
        except Exception as e:
            raise InvalidEpubError(f"Failed to load EPUB: {str(e)}")

    def extract_chapter_number(self, item):
        """
        Extracts the real chapter number from the item's title, content, or filename.

        Prioritizes filename, then title, then <title> tag in content, then content text.

        Returns:
            tuple: (int or None, str, str) - The real chapter number, method used, source text.
        """
        filename = item.get_name()
        logging.debug(f"Extracting chapter number for item: {filename}")

        # Check filename first: match '_(\d+)_'
        filename_match = re.search(r'_(\d+)_', filename)
        logging.debug(f"Filename regex match: {filename_match}")
        if filename_match:
            extracted = int(filename_match.group(1))
            logging.debug(f"Extracted from filename: {extracted}")
            return extracted, 'filename', filename
        else:
            logging.debug("Filename does not match '_(\\d+)_', falling back to title")

        # Else, check title: match '^(\d+):'
        logging.debug(f"item.title exists: {item.title is not None}, value: {item.title}")
        if item.title:
            title_match = re.match(r'^(\d+):', item.title.strip())
            logging.debug(f"Title regex match: {title_match}")
            if title_match:
                extracted = int(title_match.group(1))
                logging.debug(f"Extracted from title: {extracted}")
                return extracted, 'title', item.title.strip()
            else:
                logging.debug("Title exists but does not match regex '^(\\d+):', falling back")
        else:
            logging.debug("No item.title, falling back to <title> tag")

        # Else, parse content for <title> tag
        content = item.get_content().decode('utf-8', errors='ignore')
        title_tag_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
        logging.debug(f"<title> tag found: {title_tag_match is not None}, full match: {title_tag_match.group(0) if title_tag_match else None}, extracted text: {title_tag_match.group(1).strip() if title_tag_match else None}")
        if title_tag_match:
            title_text = title_tag_match.group(1).strip()
            num_match = re.match(r'^(\d+):', title_text)
            logging.debug(f"<title> text regex match: {num_match}")
            if num_match:
                extracted = int(num_match.group(1))
                logging.debug(f"Extracted from <title> tag: {extracted}")
                return extracted, 'title_tag', title_text
            else:
                logging.debug("<title> tag found but text does not match regex, falling back")
        else:
            logging.debug("No <title> tag found, falling back to content")

        # Else, parse content text for "Chapter (\d+)" in first 200 chars
        content_start = content[:200]
        content_match = re.match(r'^Chapter (\d+)', content_start, re.IGNORECASE)
        logging.debug(f"Content regex match: {content_match}")
        if content_match:
            extracted = int(content_match.group(1))
            logging.debug(f"Extracted from content: {extracted}")
            return extracted, 'content', content_start
        else:
            logging.debug("No '^Chapter (\\d+)' found in first 200 chars of content")

        logging.info(f"No chapter number extracted for {filename}")
        return None, 'none', ''

    def get_chapters(self):
        """
        Retrieves filtered chapter items from the EPUB, excluding non-chapter files.

        Returns:
            list: List of EpubHtml items representing actual chapters.
        """
        chapters = []
        # Get spine entries
        spine_ids = [spine_entry[0] for spine_entry in self.book.spine]
        logging.debug(f"Spine IDs: {spine_ids}")
        # Get HTML items from spine that have HTML media types
        html_media_types = ['application/xhtml+xml', 'text/html']
        exclusion_keywords = ['cover', 'info', 'toc', 'contents', 'copyright', 'acknowledgment']
        for spine_id in spine_ids:
            item = self.book.get_item_with_id(spine_id)
            if item and item.media_type in html_media_types:
                filename = item.get_name()
                logging.debug(f"Processing spine item: {filename}")
                # Check for exclusion keywords in filename
                if any(kw in filename.lower() for kw in exclusion_keywords):
                    logging.debug(f"Excluded file: {filename}, reason: contains exclusion keyword")
                    continue
                # Get content and check word count
                content = item.get_content().decode('utf-8', errors='ignore')
                content_no_tags = re.sub(r'<[^>]+>', '', content)
                words = content_no_tags.split()
                word_count = len(words)
                if word_count < 100:
                    logging.debug(f"Excluded file: {filename}, reason: content too short ({word_count} words)")
                    continue
                # Check if it appears to be a chapter
                is_chapter = re.match(r'^\d+', filename) or 'chapter' in filename.lower()
                if not (is_chapter or word_count >= 200):
                    logging.debug(f"Excluded file: {filename}, reason: does not appear to be a chapter (no numeric prefix, no 'chapter' in name, and content not substantial)")
                    continue
                logging.debug(f"Including chapter: {filename}")
                chapters.append(item)

        logging.debug(f"Filtered chapters: {[item.get_name() for item in chapters]}")
        logging.debug(f"Final chapters count: {len(chapters)}")
        return chapters

    def get_chapter_title(self, chapter_num):
        """
        Gets the title of the specified chapter.

        Args:
            chapter_num (int): Chapter number (1-based).

        Returns:
            str: Chapter title.

        Raises:
            ChapterNotFoundError: If chapter not found.
        """
        if 1 <= chapter_num <= len(self.chapters):
            item = self.chapters[chapter_num - 1]
            # Try to get title from item, fallback to filename or generic
            title = item.title
            if not title:
                # Extract from content if possible (basic)
                content = item.get_content().decode('utf-8', errors='ignore')
                # Try <title> tag first
                match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                else:
                    # Simple title extraction (first h1, h2, etc.)
                    match = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
            if not title:
                real_num = self.get_real_chapter_number(chapter_num - 1)
                title = f"Chapter {real_num if real_num is not None else chapter_num}"
            return title
        else:
            raise ChapterNotFoundError(f"Chapter {chapter_num} not found")

    def get_chapter_content(self, chapter_num):
        """
        Gets the raw HTML content of the specified chapter.

        Args:
            chapter_num (int): Chapter number (1-based).

        Returns:
            str: Raw HTML content.

        Raises:
            ChapterNotFoundError: If chapter not found.
        """
        if 1 <= chapter_num <= len(self.chapters):
            item = self.chapters[chapter_num - 1]
            return item.get_content().decode('utf-8', errors='ignore')
        else:
            raise ChapterNotFoundError(f"Chapter {chapter_num} not found")

    def get_total_chapters(self):
        """
        Returns the total number of chapters.
        """
        return len(self.chapters)

    def save_epub_with_suffix(self, output_path):
        """
        Saves the current EPUB book to the specified path.

        Args:
            output_path (str): Path where to save the EPUB.

        Raises:
            InvalidEpubError: If saving fails.
        """
        try:
            epub.write_epub(output_path, self.book, {})
            logging.info(f"EPUB saved to: {output_path}")
        except Exception as e:
            raise InvalidEpubError(f"Failed to save EPUB: {str(e)}")

    def apply_search_replace_to_epub(self, terms):
        """
        Applies search-replace terms to HTML content items in the EPUB, excluding non-content files.
        Uses configurable parallel processing and content filtering for improved performance.

        Args:
            terms (list): List of validated term dictionaries.

        Returns:
            int: Number of items processed.
        """
        from search_replace_processor import apply_search_replace

        # Retrieve performance settings from config
        enable_parallel_processing = get_setting('enable_parallel_processing')
        enable_content_filtering = get_setting('enable_content_filtering')
        min_word_count_threshold = get_setting('min_word_count_threshold')
        exclusion_keywords = get_setting('exclusion_keywords') or ['cover', 'info', 'toc', 'contents', 'copyright', 'acknowledgment']

        # Collect processable items
        processable_items = []
        items = list(self.book.get_items())
        logging.debug(f"Total items in EPUB: {len(items)}")

        for item in items:
            if item.media_type in ['application/xhtml+xml', 'text/html']:
                filename = item.get_name()
                # Check for exclusion keywords in filename
                if any(kw in filename.lower() for kw in exclusion_keywords):
                    logging.debug(f"Skipped non-content file: {filename}, reason: contains exclusion keyword")
                    continue
                if enable_content_filtering:
                    # Content filtering: check word count
                    content = item.get_content().decode('utf-8', errors='ignore')
                    content_no_tags = re.sub(r'<[^>]+>', '', content)
                    words = content_no_tags.split()
                    word_count = len(words)
                    if word_count < min_word_count_threshold:
                        logging.debug(f"Skipped file: {filename}, reason: content too short ({word_count} words)")
                        continue
                else:
                    content = item.get_content().decode('utf-8', errors='ignore')
                processable_items.append((item, filename, content))

        logging.info(f"Found {len(processable_items)} processable HTML items for term replacement")

        if not processable_items:
            return 0

        # Define helper function for processing individual items
        def process_item(item_data):
            item, filename, content = item_data
            try:
                logging.info(f"Processing item: {filename}")
                replaced_content = apply_search_replace(content, terms)
                if replaced_content != content:
                    # Ensure thread-safe content update
                    item.set_content(replaced_content.encode('utf-8'))
                    logging.debug(f"Applied replacements to item: {filename}")
                    return True  # Indicates content was modified
                return False
            except Exception as e:
                logging.error(f"Error processing item {filename}: {str(e)}")
                return False

        # Use ThreadPoolExecutor for parallel processing if enabled
        processed_count = 0

        if enable_parallel_processing:
            max_workers = get_setting('max_workers') or min(os.cpu_count() or 4, len(processable_items))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_item = {executor.submit(process_item, item_data): item_data[1] for item_data in processable_items}

                # Process completed tasks
                for future in concurrent.futures.as_completed(future_to_item):
                    filename = future_to_item[future]
                    try:
                        was_modified = future.result()
                        processed_count += 1
                        if processed_count % 10 == 0 or processed_count == len(processable_items):
                            logging.info(f"Progress: {processed_count}/{len(processable_items)} items processed")
                    except Exception as e:
                        logging.error(f"Error processing item {filename}: {str(e)}")
                        processed_count += 1  # Still count as processed even if failed
        else:
            # Sequential processing
            for item_data in processable_items:
                filename = item_data[1]
                try:
                    was_modified = process_item(item_data)
                    processed_count += 1
                    if processed_count % 10 == 0 or processed_count == len(processable_items):
                        logging.info(f"Progress: {processed_count}/{len(processable_items)} items processed")
                except Exception as e:
                    logging.error(f"Error processing item {filename}: {str(e)}")
                    processed_count += 1  # Still count as processed even if failed

        logging.info(f"Completed processing: {processed_count} HTML items processed for term replacement")
        return processed_count
    def get_real_chapter_number(self, index):
        """
        Returns the real chapter number for the given sequential index (0-based).

        Args:
            index (int): Sequential index (0-based).

        Returns:
            int or None: Real chapter number, or None if not available.
        """
        if 0 <= index < len(self.real_chapter_numbers):
            return self.real_chapter_numbers[index]
        return None

    def get_real_chapter_range(self):
        """
        Returns the range of real chapter numbers as a string, e.g., "270-293".

        Returns:
            str: Range string, or empty if no real numbers.
        """
        real_nums = [num for num in self.real_chapter_numbers if num is not None]
        if not real_nums:
            return ""
        min_num = min(real_nums)
        max_num = max(real_nums)
        if min_num == max_num:
            return str(min_num)
        return f"{min_num}-{max_num}"