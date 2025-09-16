from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
import re
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    # Remove script, style, and other unwanted tags
    for tag in soup(["script", "style", "meta", "link"]):
        tag.extract()
    # Get text content
    text = soup.get_text(separator='\n')
    print(f"After get_text: {repr(text)}")
    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
    print(f"After re.sub paragraph: {repr(text)}")
    text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces
    print(f"After normalize spaces: {repr(text)}")
    # Mock settings
    remove_line_breaks = False
    preserve_paragraph_breaks = True
    remove_empty_lines = False
    # Handle paragraph preservation based on config
    if remove_line_breaks:
        text = text.replace('\n', ' ')
        text = re.sub(r' +', ' ', text)
    elif not preserve_paragraph_breaks:
        text = text.replace('\n', ' ')
        text = re.sub(r' +', ' ', text)
    # Handle empty line removal
    if remove_empty_lines:
        # Remove multiple consecutive empty lines, preserving paragraph structure
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    print(f"Final text: {repr(text)}")
    return text.strip()

html = "<p>Para 1</p><p>\n\n\n</p><p>Para 2</p>"
soup = BeautifulSoup(html, 'lxml')
elements = soup.find_all('p')
texts = [el.get_text() for el in elements]
print("Texts:", [repr(t) for t in texts])
joined = '\n'.join(texts)
print("Joined:", repr(joined))
text = extract_text_from_html(html)
print(repr(text))