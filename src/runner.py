import os
import yaml
import logging
from src.parser import PDFParser
from src.orchestrator import LLMOrchestrator, GeminiProvider

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PipelineRunner:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.parser = PDFParser()
        
        # Get provider configuration
        provider_name = self.config.get("llm_provider", "gemini")
        api_key = self.config.get("api_key") or os.environ.get("GOOGLE_API_KEY")
        
        if provider_name == "gemini":
            if not api_key:
                logger.warning("No API key found for Gemini provider. It might fail if an actual LLM call is made.")
            provider = GeminiProvider(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

        self.orchestrator = LLMOrchestrator(provider=provider)
        
        logger.info(f"PipelineRunner initialized with provider: {provider_name}")

    def _load_config(self, path: str) -> dict:
        if not os.path.exists(path):
            logger.warning(f"Config file {path} not found. Using defaults.")
            return {"data_repo_path": "./data", "llm_provider": "gemini"}
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def run(self, input_pdf_path: str, output_dir: str):
        logger.info(f"Starting pipeline for: {input_pdf_path}")
        
        try:
            # 1. Parse
            logger.info("Step 1: Parsing PDF...")
            blocks = self.parser.extract_content(input_pdf_path)
            logger.info(f"Successfully extracted {len(blocks)} blocks.")

            # 2. Orchestrate
            logger.info("Step 2: Orchestrating LLM processing...")
            markdown_content = self.orchestrator.process_blocks(blocks)
            logger.info("LLM processing complete.")

            # 3. Save
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}.md")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            logger.info(f"Pipeline completed successfully. Output saved to: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python src/runner.py <input_pdf> <output_dir>")
    else:
        runner = PipelineRunner("config/settings.yaml")
        runner.run(sys.argv[1], sys.argv[2])
