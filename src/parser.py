import pdfplumber
import os
import statistics

class PDFParser:
    """
    A parser for extracting structured blocks from PDF files.
    """

    def extract_content(self, file_path: str) -> list[dict]:
        """
        Extracts structured blocks (paragraphs, headers, tables, etc.) from a PDF file.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            list[dict]: A list of blocks, each being a dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a PDF.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' was not found.")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("The provided file is not a PDF.")

        blocks = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_blocks = self._parse_page(page, page_num)
                    blocks.extend(page_blocks)

        except Exception as e:
            raise RuntimeError(f"An error occurred while parsing the PDF: {e}")

        return blocks

    def _parse_page(self, page, page_num: int) -> list[dict]:
        """
        Parses a single page into structured blocks.
        """
        tables = page.find_tables()
        table_bboxes = [t.bbox for t in tables]
        
        elements = []

        # 1. Add tables as elements
        for table in tables:
            data = table.extract()
            elements.append({
                "type": "table",
                "content": self._clean_table_data(data),
                "bbox": table.bbox,
                "top": table.bbox[1],
                "x0": table.bbox[0],
                "width": table.bbox[2] - table.bbox[0]
            })

        # 2. Get text elements
        words = page.extract_words()
        # Filter words inside tables
        filtered_words = []
        for w in words:
            word_bbox = (w['x0'], w['top'], w['x1'], w['bottom'])
            if not any(self._is_inside(word_bbox, tb) for tb in table_bboxes):
                filtered_words.append(w)

        if filtered_words:
            # Sort words by top, then x0
            filtered_words.sort(key=lambda w: (w['top'], w['x0']))
            
            # Group words into lines
            lines = []
            if filtered_words:
                current_line = [filtered_words[0]]
                for i in range(1, len(filtered_words)):
                    w = filtered_words[i]
                    prev_w = filtered_words[i-1]
                    
                    # If top is similar AND it's not a large horizontal gap, it's the same line.
                    # We use a threshold of 20% of page width to distinguish between a 
                    # single line and a gap between columns.
                    horizontal_gap = w['x0'] - prev_w['x1']
                    if abs(w['top'] - prev_w['top']) < 3 and horizontal_gap < page.width * 0.2:
                        current_line.append(w)
                    else:
                        lines.append(current_line)
                        current_line = [w]
                lines.append(current_line)

            # Determine page-wide median font size for header detection
            page_font_sizes = [c['size'] for c in page.chars]
            median_font_size = statistics.median(page_font_sizes) if page_font_sizes else 10

            for line_words in lines:
                line_text = " ".join(w['text'] for w in line_words)
                x0 = min(w['x0'] for w in line_words)
                top = min(w['top'] for w in line_words)
                x1 = max(w['x1'] for w in line_words)
                bottom = max(w['bottom'] for w in line_words)
                bbox = (x0, top, x1, bottom)
                
                # Default type
                line_type = "paragraph"

                # Header detection
                line_chars = [c for c in page.chars if c['x0'] >= x0 - 1 and c['x1'] <= x1 + 1 and c['top'] >= top - 1 and c['bottom'] <= bottom + 1]
                if line_chars:
                    avg_font_size = sum(c['size'] for c in line_chars) / len(line_chars)
                    if avg_font_size > median_font_size * 1.2:
                        line_type = "header"

                # List item detection
                if line_text.strip().startswith(('-', '•', '*', '1.', '2.', '3.')):
                    line_type = "list_item"

                elements.append({
                    "type": line_type,
                    "content": line_text,
                    "bbox": bbox,
                    "top": top,
                    "x0": x0,
                    "width": x1 - x0
                })

        if not elements:
            return []

        # 3. Sort all elements to handle columns
        # We'll use a simple column detection based on x0.
        # We'll group elements into columns if they have similar x0 or if they are wide enough to span columns.
        
        # First, identify columns using only text elements (or at least highly likely to be columns)
        text_x0s = sorted([e['x0'] for e in elements if e['type'] != 'table'])
        
        column_starts = []
        if text_x0s:
            column_starts.append(text_x0s[0])
            threshold = 50
            for i in range(1, len(text_x0s)):
                if text_x0s[i] - text_x0s[i-1] > threshold:
                    column_starts.append(text_x0s[i])
        
        # Assign elements to columns
        # A block is "full-width" if it spans more than, say, 60% of the page width
        page_width = page.width
        
        elements_with_col = []
        for e in elements:
            if e['width'] > page_width * 0.6:
                # Full-width block, assign to a special column index -1
                elements_with_col.append((-1, e))
            else:
                # Find the closest column start
                col_idx = 0
                min_dist = float('inf')
                for idx, start in enumerate(column_starts):
                    dist = abs(e['x0'] - start)
                    if dist < min_dist:
                        min_dist = dist
                        col_idx = idx
                elements_with_col.append((col_idx, e))

        # Sort by column index, then top. Full-width blocks (-1) should be handled carefully.
        # Actually, if we want full-width blocks to be interspersed correctly, 
        # we should sort by top, then if top is similar, by column.
        # But a full-width block might have a 'top' that is between two elements of different columns.
        
        # Let's use a simpler approach: sort everything by top.
        # If two elements have very similar top, sort by column index.
        # This is better for multi-column layouts where a full-width header might be at the top.
        
        elements_with_col.sort(key=lambda x: (x[1]['top'], x[0]))

        # 4. Final format conversion
        final_blocks = []
        for _, e in elements_with_col:
            final_blocks.append({
                "type": e["type"],
                "content": e["content"],
                "metadata": {
                    "page": page_num,
                    "bbox": e["bbox"]
                }
            })
        return final_blocks

    def _is_inside(self, bbox1, bbox2):
        return (bbox1[0] >= bbox2[0] - 0.5 and 
                bbox1[1] >= bbox2[1] - 0.5 and 
                bbox1[2] <= bbox2[2] + 0.5 and 
                bbox1[3] <= bbox2[3] + 0.5)

    def _clean_table_data(self, data):
        cleaned = []
        for row in data:
            cleaned_row = []
            for cell in row:
                if cell:
                    cleaned_cell = " ".join(cell.split())
                    cleaned_row.append(cleaned_cell)
                else:
                    cleaned_row.append("")
            cleaned.append(cleaned_row)
        return cleaned
