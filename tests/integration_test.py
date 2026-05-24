import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.runner import PipelineRunner

class TestPipelineIntegration(unittest.TestCase):
    def setUp(self):
        self.config_path = "config/settings.yaml"
        self.output_dir = "test_output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.runner = PipelineRunner(self.config_path)

    def tearDown(self):
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    @patch('src.parser.PDFParser.extract_content')
    @patch('src.orchestrator.LLMOrchestrator.process_blocks')
    def test_full_workflow(self, mock_process, mock_extract):
        # Setup mocks
        mock_extract.return_value = [
            {"type": "header", "content": "Test Header", "metadata": {"page": 1, "bbox": (0,0,10,10)}},
            {"type": "paragraph", "content": "Test content.", "metadata": {"page": 1, "bbox": (0,10,10,20)}}
        ]
        mock_process.return_value = "# Test Wiki\n\n[[Test Header]]\n\nTest content."

        # Run
        input_pdf = "dummy.pdf"
        # We need to mock os.path.exists to return True for dummy.pdf
        with patch('os.path.exists', return_value=True):
            output_file = self.runner.run(input_pdf, self.output_dir)

        # Assertions
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn("# Test Wiki", content)
            self.assertIn("[[Test Header]]", content)
        
        print("Integration test passed successfully!")

if __name__ == '__main__':
    unittest.main()