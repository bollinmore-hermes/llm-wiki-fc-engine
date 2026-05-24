import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
from src.runner import PipelineRunner

class TestPipelineRunner(unittest.TestCase):
    def setUp(self):
        self.input_pdf = "test_input.pdf"
        self.output_dir = "test_output"
        
    @patch("src.runner.PDFParser")
    @patch("src.runner.GeminiProvider")
    @patch("src.runner.LLMOrchestrator")
    @patch("os.environ.get")
    def test_run_success(self, mock_env_get, mock_orchestrator, mock_gemini, mock_parser):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.extract_content.return_value = [{"type": "paragraph", "content": "test content"}]
        
        mock_orchestrator_instance = mock_orchestrator.return_value
        mock_orchestrator_instance.process_blocks.return_value = "# Test Markdown"

        # Initialize runner
        runner = PipelineRunner()

        # Run pipeline
        with patch("os.makedirs") as mock_makedirs:
            with patch("builtins.open", mock_open()) as mocked_file:
                runner.run(self.input_pdf, self.output_dir)

        # Verifications
        mock_parser_instance.extract_content.assert_called_once_with(self.input_pdf)
        mock_orchestrator_instance.process_blocks.assert_called_once_with([{"type": "paragraph", "content": "test content"}])
        
        # Check if file was written
        expected_output_file = os.path.join(self.output_dir, "test_input.md")
        mocked_file.assert_called_with(expected_output_file, 'w', encoding='utf-8')

    @patch("src.runner.PDFParser")
    @patch("src.runner.GeminiProvider")
    @patch("src.runner.LLMOrchestrator")
    @patch("os.environ.get")
    def test_run_file_not_found(self, mock_env_get, mock_orchestrator, mock_gemini, mock_parser):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.extract_content.side_effect = FileNotFoundError("File not found")

        # Initialize runner
        runner = PipelineRunner()

        # Run pipeline
        with self.assertRaises(FileNotFoundError):
            runner.run("non_existent.pdf", self.output_dir)

if __name__ == "__main__":
    unittest.main()
