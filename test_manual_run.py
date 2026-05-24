import os
import sys
import logging

# Add the project root to sys.path to allow importing from 'src'
project_root = "/Users/chenwensheng/hermes-coder/llm-wiki-fc-engine"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.runner import PipelineRunner

# Setup logging to see everything in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    input_pdf = "/Users/chenwensheng/.hermes/profiles/main-test/cache/documents/doc_94656c557f88_document.pdf"
    output_dir = os.path.join(project_root, "test_output")
    config_path = os.path.join(project_root, "config/settings.yaml")

    # Ensure input file exists
    if not os.path.exists(input_pdf):
        logger.error(f"Input PDF not found at: {input_pdf}")
        return

    logger.info("Starting Manual End-to-End Test...")
    logger.info(f"Input PDF: {input_pdf}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info(f"Config Path: {config_path}")

    try:
        # Initialize Runner
        # Note: PipelineRunner handles config loading and provider setup
        runner = PipelineRunner(config_path)
        
        # Run Pipeline
        output_file = runner.run(input_pdf, output_dir)
        
        logger.info("========================================")
        logger.info(f"TEST SUCCESSFUL!")
        logger.info(f"Output file generated: {output_file}")
        logger.info("========================================")

        # Verify Content
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content_preview = f.read(1000) # Read first 1000 chars
            
            print("\n--- Markdown Content Preview (First 1000 chars) ---")
            print(content_preview)
            print("---------------------------------------------------\n")
        else:
            logger.error("Output file was reported as created, but does not exist on disk.")

    except Exception as e:
        logger.error("========================================")
        logger.error(f"TEST FAILED!")
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error("========================================")

if __name__ == "__main__":
    main()
