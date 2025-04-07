# Legal Document Simplification System

A Streamlit-based application that uses local AI models to simplify complex legal documents into easy-to-understand language. The system also supports translation to multiple languages and document export in various formats.

## Features

- **Legal Document Simplification**: Convert complex legal language into plain, easy-to-understand text
- **Translation Support**: Translate simplified content to Hindi and Marathi
- **Document History**: Save and access previous simplifications
- **Multiple File Formats**: Support for text, Word, and PDF documents
- **Export Options**: Export processed documents as PDF, Word, or text files
- **Privacy-Focused**: All processing happens locally on your machine using Ollama

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.com) for running local AI models
- At least 8GB RAM (16GB+ recommended)
- 10GB+ free disk space for model storage

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/Mihir-Panjikar/Legal_Document_Simplication_System.git
cd Legal_Document_Simplication_System
```

### Step 2: Create and activate a virtual environment

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install required packages

```bash
pip install -r requirements.txt
```

### Step 4: Install and set up Ollama

1. Download and install Ollama from [ollama.com](https://ollama.com)
2. Start the Ollama server:
   ```bash
   ollama serve
   ```
3. Pull at least one AI model:
   ```bash
   # Recommended model for legal document simplification
   ollama pull deepseek-r1
   
   # Alternative models
   ollama pull llama3
   ollama pull mistral
   ollama pull phi3
   ```

## Running the Application

Start the Streamlit application:

```bash
streamlit run legal_doc_simplifier.py
```

This will launch the application in your default web browser, typically at http://localhost:8501.

## Using the Application

### Step 1: Prepare your document

You can either:
- Paste text directly into the input area
- Upload a document file (TXT, DOCX, or PDF)

### Step 2: Simplify the document

1. Click the "Simplify" button
2. The application will process the document using the selected AI model
3. The simplified version will appear below

### Step 3: Translate (optional)

1. Select a target language from the dropdown (Hindi or Marathi)
2. Click "Translate"
3. The translated text will appear in the output area

### Step 4: Export (optional)

You can export your document in several formats:
- PDF
- Word Document
- Text File

### Step 5: History management

- All processed documents are saved in the history sidebar
- Click on any previous document to reload it
- Use the delete option to remove unwanted entries

## Troubleshooting

### Ollama Connection Issues

If you experience problems connecting to Ollama:

1. Check if Ollama is running:
   ```bash
   # In a new terminal window
   ollama serve
   ```

2. Verify model availability:
   ```bash
   ollama list
   ```

3. Test API connection:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Model Performance

- Larger models like llama3 provide better results but require more system resources
- If you experience slow performance, try using a smaller model
- For translation tasks, larger models are recommended for better accuracy

## Project Structure

```
Legal_Document_Simplication_System/
├── app/                      # Application components
│   ├── __init__.py
│   ├── database_operations.py
│   ├── processors.py
│   ├── session_manager.py
│   └── ui_components.py
├── data/                     # Database storage (created automatically)
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── database.py
│   ├── document_export.py
│   ├── file_extractor.py
│   ├── formatter.py
│   ├── ollama_config.py
│   ├── Simplification.py
│   └── translation.py
├── legal_doc_simplifier.py   # Main entry point
└── requirements.txt          # Project dependencies
```

## License

This project is licensed under the CC BY-NC-SA 4.0 License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- AI processing powered by [Ollama](https://ollama.com)
- Documents processed using DeepSeek-R1 and Llama models

---

Created by Mihir Panjikar as part of a final year project.