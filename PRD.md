# Product Requirements Document (PRD)

## EPUB Chapter Extraction Tool

### 1. Product Overview

#### 1.1 Product Name

**ChapterClip** (or chosen repository name)

#### 1.2 Product Description

A Python CLI tool that extracts and copies a user-defined word count from EPUB files starting from a specified chapter. The tool provides a clean, HTML-free text extraction that automatically calculates and includes complete chapters up to a maximum word limit.

#### 1.3 Vision Statement

To provide readers with an efficient way to extract and copy manageable portions of their EPUB books for reading, note-taking, or text processing purposes.

### 2. Target Users

#### 2.1 Primary Users

- **Digital readers** who want to extract specific portions of books
- **Students** needing to copy text segments for study purposes
- **Researchers** extracting book content for analysis
- **Content creators** who need clean text from EPUBs

#### 2.2 User Personas

**Persona 1: Academic Reader**

- Reads multiple EPUBs for research
- Needs specific word counts for daily reading goals
- Wants clean text without formatting distractions

**Persona 2: Language Learner**

- Reads foreign language EPUBs
- Needs manageable chunks for translation/study
- Requires consistent word count portions

### 3. Core Features & Requirements

#### 3.1 Functional Requirements

##### F1: EPUB File Selection

- **F1.1**: GUI file picker dialog for EPUB selection
- **F1.2**: Support for standard EPUB formats (EPUB 2.0, 3.0)
- **F1.3**: File validation to ensure valid EPUB structure

##### F2: Chapter Selection

- **F2.1**: Numeric input for chapter number
- **F2.2**: Chapter title display for confirmation
- **F2.3**: User confirmation prompt before processing
- **F2.4**: Error handling for invalid chapter numbers

##### F3: Word Count Configuration

- **F3.1**: Default word count of 20,000 words
- **F3.2**: User-configurable maximum word count
- **F3.3**: Persistent settings storage in config file
- **F3.4**: CLI option to modify word count settings

##### F4: Text Extraction

- **F4.1**: Extract complete chapters only (no partial chapters)
- **F4.2**: Remove all HTML tags and elements
- **F4.3**: Preserve paragraph breaks and basic formatting
- **F4.4**: Calculate cumulative word count across chapters
- **F4.5**: Stop before exceeding maximum word count

##### F5: Output Management

- **F5.1**: Direct copy to system clipboard
- **F5.2**: Success confirmation message
- **F5.3**: Display extraction summary (chapters included, total words)

##### F6: User Interface

- **F6.1**: Interactive CLI menu system
- **F6.2**: Clear option numbering
- **F6.3**: Input validation and error messages
- **F6.4**: Progress indicators for processing

#### 3.2 Non-Functional Requirements

##### N1: Performance

- **N1.1**: Process standard EPUB (<10MB) in under 5 seconds
- **N1.2**: Efficient memory usage for large EPUBs

##### N2: Usability

- **N2.1**: Intuitive menu navigation
- **N2.2**: Clear error messages
- **N2.3**: Minimal user input required

##### N3: Compatibility

- **N3.1**: Python 3.8+ support
- **N3.2**: Cross-platform (Windows, macOS, Linux)
- **N3.3**: UTF-8 encoding support

### 4. Technical Specifications

#### 4.1 Technology Stack

- **Language**: Python 3.8+
- **EPUB Processing**: `ebooklib` or `epub-reader`
- **HTML Parsing**: `BeautifulSoup4`
- **File Dialog**: `tkinter.filedialog`
- **Clipboard**: `pyperclip`
- **CLI Framework**: `click` or `rich`
- **Configuration**: `configparser` or `pyyaml`

#### 4.2 Project Structure

```
chapterclip/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── epub_processor.py
│   ├── text_extractor.py
│   ├── config_manager.py
│   ├── ui_manager.py
│   └── clipboard_handler.py
├── config/
│   └── default_config.yaml
├── tests/
│   └── test_*.py
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE
```

#### 4.3 Configuration Schema

```yaml
settings:
  max_words: 20000
  include_chapter_titles: true
  preserve_paragraph_breaks: true
  last_epub_directory: ""
```

### 5. User Flow

#### 5.1 Main Flow

1. **Launch Application**

   - Display welcome message
   - Show main menu

2. **Main Menu Options**

   - [1] Extract chapters from EPUB
   - [2] Configure settings
   - [3] View current settings
   - [4] Exit

3. **Chapter Extraction Flow**

   - Select "Extract chapters"
   - File picker opens → User selects EPUB
   - System loads and validates EPUB
   - Prompt: "Enter the chapter number you're currently reading:"
   - User inputs number (e.g., "17")
   - Display: "Chapter 17: [Chapter Title]. Is this correct? (y/n)"
   - If yes → Process extraction
   - Calculate chapters needed for word count
   - Extract and clean text
   - Copy to clipboard
   - Display: "Successfully copied chapters 17-24 (19,850 words) to clipboard!"

4. **Settings Configuration Flow**
   - Select "Configure settings"
   - Show settings menu
   - User selects setting to modify
   - Input new value
   - Validate and save to config

### 6. User Interface Mockups

#### 6.1 Main Menu

```
═══════════════════════════════════════════
        ChapterClip - EPUB Text Extractor
═══════════════════════════════════════════

Please select an option:

  [1] Extract chapters from EPUB
  [2] Configure settings
  [3] View current settings
  [4] Exit

Enter your choice (1-4): _
```

#### 6.2 Chapter Confirmation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Selected Chapter Confirmation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chapter 17: "The Journey Continues"

Is this the correct chapter? (y/n): _
```

#### 6.3 Extraction Result

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Extraction Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Successfully extracted and copied to clipboard

Details:
  • Chapters included: 17-24 (8 chapters)
  • Total words: 19,850
  • Maximum allowed: 20,000

Press Enter to return to main menu...
```

### 7. Success Metrics

- **Extraction Accuracy**: 100% clean text (no HTML remnants)
- **Word Count Precision**: Within 5% of target maximum
- **User Task Completion**: <30 seconds from launch to clipboard
- **Error Rate**: <1% failed extractions

### 8. Dependencies & Installation

#### 8.1 Required Python Packages

```txt
ebooklib>=0.18
beautifulsoup4>=4.11.0
pyperclip>=1.8.2
click>=8.1.0
rich>=13.0.0
pyyaml>=6.0
lxml>=4.9.0
```

#### 8.2 Installation Instructions

```bash
# Clone repository
git clone https://github.com/username/chapterclip.git

# Install dependencies
pip install -r requirements.txt

# Run application
python -m chapterclip
```

### 9. Error Handling

#### 9.1 Error Scenarios

- **Invalid EPUB file**: Display error and return to file selection
- **Chapter not found**: Show available chapter range
- **Clipboard access denied**: Offer alternative (show text in terminal)
- **Corrupted EPUB structure**: Graceful degradation with warning

### 10. Future Enhancements

- **v2.0 Features**:
  - Multiple EPUB batch processing
  - Export to various formats (TXT, MD, DOCX)
  - Reading progress tracking
  - Chapter bookmarking
  - Custom extraction patterns (e.g., every other chapter)
  - Integration with cloud storage
  - GUI version using PyQt or Tkinter

### 11. Development Timeline

**Phase 1 (Week 1-2)**: Core functionality

- EPUB reading and parsing
- Text extraction and cleaning

**Phase 2 (Week 2-3)**: User interface

- CLI menu system
- File picker integration

**Phase 3 (Week 3-4)**: Configuration & Polish

- Settings management
- Error handling
- Testing and documentation

### 12. Acceptance Criteria

- [ ] Successfully extracts text from 95% of standard EPUB files
- [ ] Accurate word counting (±1% margin)
- [ ] Clean text output with no HTML artifacts
- [ ] Settings persist between sessions
- [ ] Cross-platform clipboard functionality
- [ ] User-friendly error messages
- [ ] Complete documentation and help system
