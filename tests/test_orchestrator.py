import unittest
from unittest.mock import MagicMock
from src.orchestrator import LLMOrchestrator, LLMProvider

class MockLLMProvider(LLMProvider):
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0

    def generate_text(self, prompt: str) -> str:
        response = self.responses[self.call_count]
        self.call_count += 1
        return response

class TestLLMOrchestrator(unittest.TestCase):
    def setUp(self):
        self.mock_blocks = [
            {"type": "paragraph", "content": "Apple Inc. reported a revenue of $90 billion."},
            {"type": "paragraph", "content": "This growth was driven by iPhone sales."}
        ]

    def test_process_blocks_workflow(self):
        # Define the responses for the two stages
        # Stage 1: Extraction (JSON)
        extraction_response = """
        ```json
        {
          "concepts": ["Apple Inc.", "iPhone sales"],
          "data_points": ["revenue of $90 billion"],
          "relations": ["iPhone sales drove revenue growth"]
        }
        ```
        """
        # Stage 2: Synthesis (Markdown)
        synthesis_response = "# Apple Inc. Wiki\n\n[[Apple Inc.]] is a company. [[iPhone sales]] are important."

        mock_provider = MockLLMProvider(responses=[extraction_response, synthesis_response])
        orchestrator = LLMOrchestrator(provider=mock_provider)

        result = orchestrator.process_blocks(self.mock_blocks)

        # Verify the workflow
        self.assertEqual(result, synthesis_response)
        self.assertEqual(mock_provider.call_count, 2)

    def test_process_blocks_no_json_blocks(self):
        # Test when LLM doesn't return JSON code blocks
        extraction_response = '{"concepts": ["A"], "data_points": [], "relations": []}'
        synthesis_response = "Markdown output"

        mock_provider = MockLLMProvider(responses=[extraction_response, synthesis_response])
        orchestrator = LLMOrchestrator(provider=mock_provider)

        result = orchestrator.process_blocks(self.mock_blocks)

        self.assertEqual(result, synthesis_response)
        self.assertEqual(mock_provider.call_count, 2)

if __name__ == "__main__":
    unittest.main()
