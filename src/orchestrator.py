import abc
import google.generativeai as genai
import json

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_text(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

class LLMOrchestrator:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.extraction_prompt = (
            "Extract key concepts, financial metrics, and causal relationships "
            "from the following text blocks. Output in JSON format with keys: "
            "'concepts', 'data_points', and 'relations'.\n\n"
            "Text blocks:\n{text_blocks}"
        )
        self.synthesis_prompt = (
            "Based on the extracted structured data, write a professional, "
            "encyclopedic Wiki article in Markdown. Use [[WikiLinks]] for all "
            "identified key concepts.\n\n"
            "Structured Data:\n{structured_data}"
        )

    def process_blocks(self, blocks: list[dict]) -> str:
        # Phase 1: Extraction
        processed_contents = []
        for b in blocks:
            content = b.get("content", "")
            if isinstance(content, list):
                # Convert list (e.g., table data) to a string representation
                # For tables, we'll convert it to a simple markdown-like string
                if content and isinstance(content[0], list):
                    # It's a 2D list (table)
                    rows = []
                    for row in content:
                        rows.append(" | ".join(row))
                    processed_contents.append("\n".join(rows))
                else:
                    # It's a 1D list
                    processed_contents.append(" ".join(map(str, content)))
            else:
                processed_contents.append(str(content))

        text_blocks_content = "\n".join(processed_contents)
        extraction_input = self.extraction_prompt.format(text_blocks=text_blocks_content)
        extracted_data_raw = self.provider.generate_text(extraction_input)
        
        # In a real scenario, we might want to parse the JSON here to validate it
        # or clean it up if the LLM includes markdown code blocks.
        # For this implementation, we'll pass the raw string to the next stage.
        # If the LLM returns ```json ... ```, we should clean it.
        extracted_data_cleaned = extracted_data_raw.strip()
        if extracted_data_cleaned.startswith("```json"):
            extracted_data_cleaned = extracted_data_cleaned.split("```json")[1].split("```")[0].strip()
        elif extracted_data_cleaned.startswith("```"):
            extracted_data_cleaned = extracted_data_cleaned.split("```")[1].split("```")[0].strip()

        # Phase 2: Synthesis
        synthesis_input = self.synthesis_prompt.format(structured_data=extracted_data_cleaned)
        wiki_markdown = self.provider.generate_text(synthesis_input)
        
        return wiki_markdown
