import pytest
import os
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

def test_parser_invalid_file_extension():
    """Tests if PDFParser raises ValueError for a non-PDF file."""
    parser = PDFParser()
    # Create a dummy non-pdf file
    dummy_file = "test_dummy.txt"
    with open(dummy_file, "w") as f:
        f.write("this is not a pdf")
    
    try:
        with pytest.raises(ValueError):
            parser.extract_content(dummy_file)
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

# Note: Testing with a real PDF would require a sample PDF file.
# For now, we ensure the basic error handling and structure are correct.
