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
        self.load_book()

    def load_book(self):
        """
        Loads the EPUB book and extracts chapters.
        """
        try:
            self.book = epub.read_epub(self.file_path)
            self.chapters = self.get_chapters()
            logging.info(f"Loaded EPUB file: {self.file_path}")
        except Exception as e:
            raise InvalidEpubError(f"Failed to load EPUB: {str(e)}")

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
                # Simple title extraction (first h1, h2, etc.)
                import re
                match = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
            if not title:
                title = f"Chapter {chapter_num}"
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

        Returns:
            int: Number of chapters.
        """
        return len(self.chapters)