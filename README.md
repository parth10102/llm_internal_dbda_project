---
title: "About Project-Unified LLM Framework"
format: html
editor: visual
---

## 🚀 Technical Overview

The system is built on a modular architecture that separates the UI, the extraction engine, the intelligence logic, and data validation.

### 1. Input Orchestration (`app.py`)

The entry point is a **Gradio-based web interface**.

-   **Hybrid Input:** It accepts raw text, web URLs, or physical files (Images, PDFs, DOCX).

-   **Real-time Processing:** The `run_analysis` function determines the input type and routes it to the appropriate extraction method in the backend.

### 2. The Extraction Engine (`main.py`)

This script handles the conversion of non-textual data into a format the AI can process:

-   **OCR (Optical Character Recognition):** Uses `pytesseract` to read text from images (JPG, PNG, etc.).

-   **Document Parsing:** Utilizes `PyPDF2` for PDF data and `python-docx` for Word documents.

-   **Web Scraping:** Uses `trafilatura` to fetch and clean content from URLs, removing noise like ads and headers.

-   **Script & Language Detection:** A custom logic layer identifies scripts based on Unicode ranges (e.g., Devanagari vs. Tamil) and uses `langid` to calculate language confidence scores.

### 3. Intelligence Logic (`config.py`)

This contains the **System Prompt**, which acts as the application's "operating manual".

-   **Master Linguist Mode:** It forces the AI to identify Romanized Indic languages (e.g., "ROMANIZED_HINDI" for "Namaste").

-   **Intelligence NER:** Implements strict rules for Entity Extraction. It distinguishes between a PERSON and an ORGANIZATION by checking for brand markers like `@Apple_India` or `@Zomato`.

-   **Domain Identification:** Restricts the AI to specific security-focused domains (Law and Order, Extremism, etc.) and filters out low-confidence results (anything ≤ 0.3).

### 4. Validation & Metrics (`schemas.py` & `main.py`)

-   **Pydantic Schemas:** Every response from the AI is validated against `AnalysisOutput` to ensure the JSON structure is intact and follows strict data types.

-   **Performance Monitoring:** The system tracks execution time and system resource usage (RAM/GPU) via `psutil`.

## 🛠️ Setup & Installation

### Prerequisites

1.  **Ollama:** [Download](https://ollama.com/) and run `ollama pull qwen2.5:7b`.

2.  **Tesseract OCR:** Install Tesseract on your OS. Update the path in `main.py`: `pytesseract.pytesseract.tesseract_cmd = r'YOUR_PATH_TO_TESSERACT.EXE'`

## 🚦 How to Use

1.  Run the application: `gradio app.py`. (Useful for hot-reloading)

2.  Open the local URL (usually `http://127.0.0.1:7860`).

3.  Choose an input method:

    -   **Text:** Paste mixed-language social media posts.

    -   **URL:** Paste a news article link.

    -   **File:** Upload a scanned document or PDF report.

4.  Click **Analyze** to generate the JSON intelligence output.
