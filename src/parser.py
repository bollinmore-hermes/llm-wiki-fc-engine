import pdfplumber
import os

class PDFParser:
    """
    A parser for extracting text and tables from PDF files.
    """

    def extract_content(self, file_path: str) -> dict:
        """
        Extracts text and tables from a PDF file.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            dict: A dictionary containing 'text' (str) and 'tables' (list of lists).

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a PDF.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' was not found.")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("The provided file is not a PDF.")

        content = {
            "text": "",
            "tables": []
        }

        try:
            with pdfplumber.open(file_path) as pdf:
                all_text = []
                all_tables = []

                for page in pdf.pages:
                    # Extract text
                    text = page.extract_text()
                    if text:
                        all_text.append(text)

                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)

                content["text"] = "\n".join(all_text)
                content["tables"] = all_tables

        except Exception as e:
            # In a real scenario, we might want to log this error or re-raise a custom exception.
            raise RuntimeError(f"An error occurred while parsing the PDF: {e}")

        return content
