# llm-wiki-fc-engine

研報 PDF 知識提取與 Markdown 轉換引擎。

## 1. 環境設定 (Configuration)

在使用引擎之前，必須配置 LLM (如 Gemini) 的 API 金鑰。

### 依賴安裝
首先，請確保已安裝 Python 環境，並安裝必要的套件：
```bash
pip install -r requirements.txt
```

### 配置 API 金鑰
*   **方法 A：使用 `.env` 檔案 (推薦)**
    在專案根目錄下建立一個 `.env` 檔案，並加入以下內容：
    ```env
    GOOGLE_API_KEY=您的_Google_Gemini_API_Key
    ```
    *請確保 `.env` 已加入 `.gitignore` 以免洩漏金鑰。*

*   **方法 B：設定環境變數**
    在 Terminal 中直接執行：
    ```bash
    export GOOGLE_API_KEY='您的_Google_Gemini_API_Key'
    ```

## 2. 啟動執行 (Execution)

您可以透過命令列直接執行 Pipeline，將 PDF 轉換為結構化的 Markdown 內容。

### 基本用法
使用 `src/runner.py` 腳本，並指定輸入的 PDF 路徑與輸出的目錄：

```bash
python src/runner.py <輸入_PDF_路徑> <輸出_目錄_路徑>
```

**範例：**
```bash
python src/runner.py ./data/sample_report.pdf ./output/
```

### 工作流程說明
執行後，引擎會執行以下三個步驟：
1.  **Parsing (解析)**：使用 `PDFParser` 提取 PDF 中的文本區塊。
2.  **Orchestrating (編排)**：將文本區塊傳送至 LLM (Gemini) 進行摘要、結構化處理與知識提取。
3.  **Saving (儲存)**：將處理後的內容儲存為同名的 `.md` 檔案。

### 自定義配置
若需修改預設行為（如 LLM 提供商或路徑設定），請編輯 `config/settings.yaml`。
