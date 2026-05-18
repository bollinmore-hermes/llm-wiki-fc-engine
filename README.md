# llm-wiki-fc-engine

Initial project scaffolding.

## Configuration

To use the Gemini provider, you must provide a Google API Key. 

**⚠️ IMPORTANT SECURITY NOTE:** Never commit your API keys to version control (e.g., GitHub).

### Recommended Setup: Using `.env` file

1.  Create a `.env` file in the project root directory.
2.  Add your key to the file:
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    ```
3.  Ensure `.env` is listed in your `.gitignore` file (it is included by default in this project).

### Alternative: Environment Variable

You can also set the `GOOGLE_API_KEY` directly in your shell:
```bash
export GOOGLE_API_KEY='your_actual_api_key_here'
```

