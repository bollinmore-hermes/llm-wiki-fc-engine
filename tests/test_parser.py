import pytest
import os
from unittest.mock import MagicMock, patch
from src.parser import PDFParser

def test_parser_initialization():
    """Tests if the PDFParser can be initialized."""
    parser = PDFParser()
    assert isinstance(parser, PDFParser)

def test_parser_file_not_found():
    """Tests if PDFParser raises FileNotFoundError for a non-existent file."""
    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.extract_content("non_existent_file.pdf")

@patch("pdfplumber.open")
def test_parser_layout_aware_reading_order(mock_open):
    """Tests if the parser correctly handles a two-column layout."""
    parser = PDFParser()
    
    # Mock Page
    mock_page = MagicMock()
    mock_page.width = 600
    mock_page.find_tables.return_value = []
    mock_page.extract_words.return_value = [
        # Column 1
        {'text': 'Col1-Line1', 'x0': 50, 'top': 100, 'x1': 150, 'bottom': 110},
        {'text': 'Col1-Line2', 'x0': 50, 'top': 150, 'x1': 150, 'bottom': 160},
        # Column 2
        {'text': 'Col2-Line1', 'x0': 350, 'top': 100, 'x1': 450, 'bottom': 110},
        {'text': 'Col2-Line2', 'x0': 350, 'top': 150, 'x1': 450, 'bottom': 160},
    ]
    mock_page.chars = [
        {'x0': 50, 'top': 100, 'x1': 150, 'bottom': 110, 'size': 10},
        {'x0': 50, 'top': 150, 'x1': 150, 'bottom': 160, 'size': 10},
        {'x0': 350, 'top': 100, 'x1': 450, 'bottom': 110, 'size': 10},
        {'x0': 350, 'top': 150, 'x1': 450, 'bottom': 160, 'size': 10},
    ]

    # Mock PDF
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    # We need to provide a real file path that exists for the os.path.exists check
    # Or we can mock os.path.exists
    with patch("os.path.exists", return_value=True):
        blocks = parser.extract_content("dummy.pdf")

    # Check reading order:
    # Since we have two columns, we expect the elements to be sorted by top.
    # If they have the same top, we want to see if they are grouped or ordered.
    # In my implementation, I sort by (top, col_idx).
    # For the same top (100), Col1 (idx 0) should come before Col2 (idx 1).
    # Wait, my implementation sorts by (top, col_idx).
    # Let's check.
    
    contents = [b['content'] for b in blocks]
    # Expected order based on (top, col_idx):
    # (100, 0) -> Col1-Line1
    # (100, 1) -> Col2-Line1
    # (150, 0) -> Col1-Line2
    # (150, 1) -> Col2-Line2
    assert contents == ['Col1-Line1', 'Col2-Line1', 'Col1-Line2', 'Col2-Line2']

@patch("pdfplumber.open")
def test_parser_enhanced_table_extraction(mock_open):
    """Tests if table data is cleaned (removing excessive newlines)."""
    parser = PDFParser()
    
    # Mock Table
    mock_table = MagicMock()
    mock_table.bbox = (50, 50, 550, 150)
    mock_table.extract.return_value = [
        ["Header1", "Header2"],
        ["Messy\nCell", "Clean Cell"]
    ]
    
    # Mock Page
    mock_page = MagicMock()
    mock_page.width = 600
    mock_page.find_tables.return_value = [mock_table]
    mock_page.extract_words.return_value = [] # No text words to avoid interference
    mock_page.chars = []

    # Mock PDF
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    with patch("os.path.exists", return_value=True):
        blocks = parser.extract_content("dummy.pdf")

    # Find the table block
    table_block = next(b for b in blocks if b['type'] == 'table')
    expected_table = [
        ["Header1", "Header2"],
        ["Messy Cell", "Clean Cell"]
    ]
    assert table_block['content'] == expected_table

@patch("pdfplumber.open")
def test_parser_block_type_detection(mock_open):
    """Tests if headers, paragraphs and list items are correctly identified."""
    parser = PDFParser()
    
    # Mock Page
    mock_page = MagicMock()
    mock_page.width = 600
    mock_page.find_tables.return_value = []
    
    # Words and chars to simulate:
    # 1. A Header (larger font)
    # 2. A Paragraph
    # 3. A List Item
    mock_page.extract_words.return_value = [
        {'text': 'Large Header', 'x0': 50, 'top': 50, 'x1': 200, 'bottom': 70},
        {'text': 'Normal paragraph text.', 'x0': 50, 'top': 100, 'x1': 300, 'bottom': 120},
        {'text': '- List item one', 'x0': 50, 'top': 150, 'x1': 200, 'bottom': 170},
    ]
    
    # To detect header, we need median font size.
    # Let's say median is 10. Header is 20.
    # We need to populate mock_page.chars
    mock_page.chars = [
        # Header chars
        {'x0': 50, 'top': 50, 'x1': 200, 'bottom': 70, 'size': 20},
        # Paragraph chars
        {'x0': 50, 'top': 100, 'x1': 300, 'bottom': 120, 'size': 10},
        # List item chars
        {'x0': 50, 'top': 150, 'x1': 200, 'bottom': 170, 'size': 10},
    ]

    # Mock PDF
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    with patch("os.path.exists", return_value=True):
        blocks = parser.extract_content("dummy.pdf")

    types = [b['type'] for b in blocks]
    contents = [b['content'] for b in blocks]
    
    assert 'header' in types
    assert 'paragraph' in types
    assert 'list_item' in types
    
    assert contents[0] == 'Large Header'
    assert contents[1] == 'Normal paragraph text.'
    assert contents[2] == '- List item one'

@patch("pdfplumber.open")
def test_parser_table_cleaning_complex(mock_open):
    """Tests if table data is cleaned with complex whitespace and multiple newlines."""
    parser = PDFParser()
    
    mock_table = MagicMock()
    mock_table.bbox = (0, 0, 100, 100)
    mock_table.extract.return_value = [
        ["  Spaced  ", "\nNew\nLine\n"],
        ["Multiple    Spaces", "Tab\tAnd\nNewline"]
    ]
    
    mock_page = MagicMock()
    mock_page.width = 100
    mock_page.find_tables.return_value = [mock_table]
    mock_page.extract_words.return_value = []
    mock_page.chars = []
    
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf
    
    with patch("os.path.exists", return_value=True):
        blocks = parser.extract_content("dummy.pdf")
    
    table_block = next(b for b in blocks if b['type'] == 'table')
    expected_table = [
        ["Spaced", "New Line"],
        ["Multiple Spaces", "Tab And Newline"]
    ]
    assert table_block['content'] == expected_table

def test_parser_invalid_file_extension():
    """Tests if PDFParser raises ValueError for a non-PDF file."""
    parser = PDFParser()
    dummy_file = "test_dummy.txt"
    with open(dummy_file, "w") as f:
        f.write("this is not a pdf")
    
    try:
        with pytest.raises(ValueError):
            parser.extract_content(dummy_file)
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

@patch("pdfplumber.open")
def test_parser_table_cleaning_requested(mock_open):
    """Tests the specific table cleaning case requested in the task."""
    parser = PDFParser()
    
    # Mock Table
    mock_table = MagicMock()
    mock_table.bbox = (0, 0, 100, 100)
    mock_table.extract.return_value = [["Cell 1", "Cell 2\nwith\nnewlines"], ["Cell 3  ", "  Cell 4"]]
    
    # Mock Page
    mock_page = MagicMock()
    mock_page.width = 100
    mock_page.find_tables.return_value = [mock_table]
    mock_page.extract_words.return_value = []
    mock_page.chars = []

    # Mock PDF
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    with patch("os.path.exists", return_value=True):
        blocks = parser.extract_content("dummy.pdf")

    # Assert
    table_block = next(b for b in blocks if b['type'] == 'table')
    expected_content = [["Cell 1", "Cell 2 with newlines"], ["Cell 3", "Cell 4"]]
    assert table_block['content'] == expected_content
