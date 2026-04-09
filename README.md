# 🧹 AI Information Overload Filter — Smart Content Cleaner

> Stop drowning in text. Paste any content and get a clean summary, key insights, and smart priority labels — instantly.

---

## ✨ Features

| Feature | Details |
|---|---|
| **AI Summarization** | Powered by `sshleifer/distilbart-cnn-12-6` — fast, lightweight, cloud-ready |
| **Smart Classification** | Labels every sentence as URGENT 🔴 / IMPORTANT 🟠 / IGNORE ⚪ |
| **Keyword Extraction** | Named entities + key noun phrases via spaCy |
| **Multi-format Input** | Plain text, `.txt` files, `.pdf` files |
| **Summary Length Control** | Short / Medium / Long |
| **Edge Case Handling** | Empty input, non-English text, oversized files, PDF errors |
| **Modern UI** | Clean, minimal, responsive Streamlit interface |

---

## 🗂️ Project Structure

```
ai_content_cleaner/
├── main.py            # Streamlit UI & orchestration
├── summarizer.py      # HuggingFace summarization pipeline
├── classifier.py      # Rule-based sentence classifier
├── preprocessing.py   # Text cleaning, tokenization, deduplication
├── utils.py           # spaCy keywords, file reading, helpers
├── requirements.txt   # Python dependencies
├── packages.txt       # System packages for Streamlit Cloud
└── README.md
```

---

## 🚀 Run Locally

### 1. Clone / download the project

```bash
git clone https://github.com/your-username/ai-content-cleaner.git
cd ai_content_cleaner
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the app

```bash
streamlit run main.py
```

The app opens at **http://localhost:8501**

---

## ☁️ Deploy on Streamlit Cloud

1. Push this folder to a **public GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in
3. Click **New app**
4. Select your repo, branch, and set the main file to `main.py`
5. Click **Deploy** — Streamlit Cloud will install everything from `requirements.txt` and `packages.txt` automatically

> **Note:** The first load takes ~60 seconds while the AI model downloads. Subsequent loads are fast thanks to caching.

---

## 📖 How It Works

```
User Input (text / .txt / .pdf)
        ↓
  Text Extraction
        ↓
  Cleaning & Preprocessing   ← remove noise, dedup, language check
        ↓
  AI Summarization           ← distilbart-cnn-12-6
        ↓
  Keyword Extraction         ← spaCy en_core_web_sm
        ↓
  Sentence Classification    ← URGENT / IMPORTANT / IGNORE
        ↓
  Structured Output Display
```

---

## ⚙️ Configuration

| Parameter | Default | Location |
|---|---|---|
| Max input size | 15,000 chars | `utils.py → MAX_TEXT_CHARS` |
| Max file upload | 5 MB | `utils.py → MAX_FILE_SIZE_MB` |
| Summarization model | `sshleifer/distilbart-cnn-12-6` | `summarizer.py → MODEL_NAME` |
| spaCy model | `en_core_web_sm` | `utils.py → load_spacy()` |

---

## 🛠️ Tech Stack

- **Streamlit** — UI framework
- **HuggingFace Transformers** — AI summarization
- **PyTorch** — Model backend (CPU)
- **spaCy** — NLP / keyword extraction
- **NLTK** — Sentence tokenization
- **PyPDF2** — PDF text extraction

---

## 📄 License

MIT — free to use, modify, and deploy.
