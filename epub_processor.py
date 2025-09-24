import logging
import re
from ebooklib import epub
from utils.error_handler import InvalidEpubError, ChapterNotFoundError

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