# Legal Document Simplification System

A Streamlit-based application that uses **Groq Cloud API** to simplify complex legal documents into easy-to-understand language. The system supports translation to multiple Indian languages and document export in various formats.

## ✨ Features

- **Legal Document Simplification**: Convert complex legal language into plain, easy-to-understand text
- **Translation Support**: Translate simplified content to Hindi and Marathi
- **Cloud-Based AI**: Powered by Groq's fast cloud inference (no local setup required)
- **Document History**: Save and access previous simplifications
- **Multiple File Formats**: Support for text, Word, and PDF documents
- **Export Options**: Export processed documents as PDF, Word, or text files
- **Fast & Free**: Uses Groq's free tier - 14,400 requests/day

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

#### Step 1: Clone the repository

```bash
git clone https://github.com/Mihir-Panjikar/Legal_Document_Simplication_System.git
cd Legal_Document_Simplication_System
```

#### Step 2: Create and activate a virtual environment

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

#### Step 3: Install required packages

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Groq API Key

**Option 1: Using Streamlit Secrets (Recommended)**

1. Copy the secrets template:
   ```bash
   cp .streamlit/secrets.toml.template .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and add your API key:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_api_key_here"
   ```

**Option 2: Using Environment Variables**

1. Copy the .env template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` and add your API key:
   ```bash
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

**Getting Your Groq API Key:**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_`)

## 🎯 Running the Application

Start the Streamlit application:

```bash
streamlit run legal_doc_simplifier.py
```

The application will launch in your default web browser at `http://localhost:8501`.

## 📖 Using the Application

### Step 1: Prepare your document

You can either:
- **Paste text** directly into the input area
- **Upload a file** (TXT, DOCX, or PDF)

### Step 2: Simplify the document

1. Add a document title (optional)
2. Click the **"Simplify Document"** button
3. The AI will process your document using Groq's cloud API
4. Simplified text appears in the output area

### Step 3: Translate (optional)

1. Select a target language from the dropdown (Hindi or Marathi)
2. Click **"Translate"**
3. The translated text will appear below

### Step 4: Export (optional)

Export your document in multiple formats:
- 📄 **PDF** - Professional document format
- 📝 **Word Document** - Editable DOCX format
- 📋 **Text File** - Plain text format

### Step 5: History management

- All processed documents are automatically saved
- Access previous documents from the history sidebar
- Click any entry to reload it
- Use the delete option (🗑️) to remove unwanted entries

## ⚙️ Advanced Settings

Click the **"Advanced"** button in the sidebar to:
- **Select AI Model**: Choose between speed (8B) and quality (70B)
- **View API Status**: Check Groq API connection
- **Monitor Rate Limits**: Track your usage

### Available Models

| Model | Speed | Best For |
|-------|-------|----------|
| **Llama 3.1 8B (Fast)** | 560 tokens/sec | General documents, quick processing |
| **Llama 3.3 70B (Quality)** | 280 tokens/sec | Complex legal documents, higher accuracy |

## 🔧 Configuration Options

### Streamlit Secrets (`.streamlit/secrets.toml`)

**Required:**
```toml
GROQ_API_KEY = "gsk_your_api_key_here"
```

**Optional** (with defaults):
```toml
GROQ_DEFAULT_MODEL = "llama-3.1-8b-instant"
GROQ_TPM_8B = 250000              # Tokens per minute
GROQ_RPM_8B = 1000                # Requests per minute
GROQ_RPD_8B = 14400               # Requests per day
MAX_TOKENS_PER_REQUEST = 4096     # Max tokens per request
API_TIMEOUT_SECONDS = 30          # Request timeout
```

See `.streamlit/secrets.toml.template` for all available options.

## 🐛 Troubleshooting

### API Key Issues

**Error: "Missing Groq API key"**

1. Check that you've created either:
   - `.streamlit/secrets.toml` with `GROQ_API_KEY`, or
   - `.env` file with `GROQ_API_KEY`
2. Verify the API key is valid (starts with `gsk_`)
3. Restart the Streamlit app after adding the key

### Connection Issues

**Error: "Unable to connect to Groq API"**

1. Check your internet connection
2. Verify your API key is active at [console.groq.com](https://console.groq.com)
3. Check if you've exceeded rate limits (14,400 requests/day on free tier)

### Rate Limit Warnings

If you see rate limit warnings:
- The app tracks your usage automatically
- Warnings appear at 80% of limit
- Free tier: 1,000 RPM, 250K-300K TPM, 14,400 RPD
- Consider using the 8B model for faster, more efficient processing

### Slow Performance

- **Use faster model**: Switch to Llama 3.1 8B in Advanced settings
- **Reduce token limit**: Lower `MAX_TOKENS_PER_REQUEST` in secrets
- **Check network**: Groq API requires good internet connection

## 📁 Project Structure

```
Legal_Document_Simplication_System/
├── 📄 legal_doc_simplifier.py   # Main application entry point
├── 📄 requirements.txt          # Python dependencies
│
├── 📁 app/                      # Application components
│   ├── __init__.py
│   ├── database_operations.py  # History & database operations
│   ├── processors.py           # Document processing logic
│   ├── session_manager.py      # Session state management
│   └── ui_components.py        # UI rendering components
│
├── 📁 utils/                    # Utility functions
│   ├── __init__.py
│   ├── groq_config.py          # ✨ Groq API configuration
│   ├── groq_inference.py       # ✨ Groq API client & inference
│   ├── Simplification.py       # Document simplification
│   ├── translation.py          # Translation utilities
│   ├── database.py             # Database utilities
│   ├── document_export.py      # Export to PDF/Word/Text
│   └── file_extractor.py       # Extract text from files
│
├── 📁 .streamlit/               # Streamlit configuration
│   ├── secrets.toml.template   # Secrets template (copy this)
│   ├── secrets.toml.minimal    # Minimal config template
│   └── README.md               # Setup instructions
│
├── 📁 assets/                   # Fonts and images
├── 📁 data/                     # Database storage (auto-created)
└── 📁 Notebook/                 # Development notebooks
```

## 🚢 Deploying to Streamlit Cloud

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Deploy Groq-powered legal simplifier"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository and branch
4. Set main file: `legal_doc_simplifier.py`
5. Click **"Deploy"**

### Step 3: Configure Secrets

1. In Streamlit Cloud dashboard, go to **Settings** → **Secrets**
2. Add your Groq API key:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_api_key_here"
   ```
3. Click **"Save"**

Your app will automatically restart with the new configuration!

## 🔐 Security Best Practices

- ✅ **Never commit** `.streamlit/secrets.toml` or `.env` to git (already in `.gitignore`)
- ✅ **Use secrets** for API keys, not environment variables in production
- ✅ **Rotate keys** if accidentally exposed
- ✅ **Monitor usage** at [console.groq.com](https://console.groq.com)
- ✅ **Use different keys** for development and production

## 🆓 Groq Free Tier Limits

| Resource | Limit |
|----------|-------|
| **Requests per Minute** | 1,000 |
| **Tokens per Minute (8B)** | 250,000 |
| **Tokens per Minute (70B)** | 300,000 |
| **Requests per Day** | 14,400 |
| **Cost** | 100% Free |

The app automatically tracks and warns you when approaching limits.

## 🛠️ Development

### Local Testing

1. Set up your API key (see Configuration section)
2. Run the app:
   ```bash
   streamlit run legal_doc_simplifier.py
   ```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests (when available)
pytest tests/
```

## 📝 License

This project is licensed under the CC BY-NC-SA 4.0 License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- AI processing powered by [Groq Cloud](https://groq.com)
- Models: Llama 3.1 & Llama 3.3 by Meta

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

**Mihir Panjikar** - Final Year Project

---

**⭐ If you find this project helpful, please give it a star!**