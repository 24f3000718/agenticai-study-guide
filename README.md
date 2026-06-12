# Academic Assistant — Subject Guide & Question Bank AI Agent

An AI-powered academic assistant that lets students upload lecture notes, textbooks, lab manuals, and past papers — then ask natural-language questions to get comprehensive, source-attributed answers.

Built for **Track A1: Computer Science Subject Guide** with multi-document RAG, CS-specific content analysis, and three response modes (Study, Exam, Quick Revision).

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-team/academic-assistant.git
cd academic-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** First run also downloads the `all-MiniLM-L6-v2` embedding model (~80 MB). This is automatic.

### 4. Set up your API key

Get a **free** Groq API key at [console.groq.com](https://console.groq.com).

```bash
cp .env.example .env
# Open .env and paste your key:
#   GROQ_API_KEY_1=gsk_your_key_here
```

You can add multiple keys (`GROQ_API_KEY_2`, `GROQ_API_KEY_3`, …) — the app rotates them automatically when rate limits are hit.

### 5. Run

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**.

---

## Usage

1. **Upload documents** — use the sidebar to upload PDFs, DOCX, PPTX, or TXT files.
2. **Select content type** — tag each file (Lecture Notes, Textbook, Past Paper, Lab Manual, etc.).
3. **Click "Process Documents"** — files are chunked, embedded, and indexed.
4. **Ask questions** — type any question in the chat area.
5. **Switch modes** using the three buttons:
   - **Study Mode** — comprehensive explanations with source attribution
   - **Exam Mode** — step-by-step solutions ready for exam submission
   - **Quick Revision** — concise bullet points for last-minute review
6. **Export** — use the sidebar Export section to download your chat as Markdown or plain text.

---

## Project Structure

```
academic-assistant/
├── app.py                        # Main Streamlit application
├── requirements.txt
├── .env.example                  # API key template
├── .streamlit/
│   └── config.toml               # Streamlit deployment config
├── components/
│   ├── chat_interface.py         # Chat UI (3-mode selector, history)
│   ├── sidebar.py                # Document upload, library, export
│   ├── progress_tracker.py       # CS subject analysis dashboard
│   └── export_manager.py         # Download chat / study notes
├── config/
│   └── settings.py               # Config, API key manager, CS subjects
├── core/
│   ├── document_processor.py     # Load & chunk PDF/DOCX/PPTX/TXT
│   ├── vector_store.py           # FAISS vector store manager
│   └── rag_chain.py              # LangChain RAG pipeline + key rotation
├── database/
│   └── db_manager.py             # SQLite: progress, sessions, study plans
├── prompts/
│   └── base_prompts.py           # Study / Exam / Quick / CS prompt templates
├── tracks/
│   ├── base_track.py             # Abstract base class for tracks
│   └── track_a1_cs.py            # CS Track: code detection, algorithm analysis
└── utils/
    ├── cs_utils.py               # Code/algorithm/DS extraction utilities
    └── text_processing.py        # Text cleaning helpers
```

---

## Deployment (Streamlit Cloud)

1. Push your repo to GitHub (make sure `.env` is in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo and set **Main file path** to `app.py`.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY_1 = "gsk_your_key_here"
   ```
5. Click **Deploy**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit 1.32 |
| LLM | Groq (Llama 3.1 8B Instant) |
| RAG Framework | LangChain 0.2 |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Vector Store | FAISS (in-memory) |
| Document Parsing | PyPDF2, python-docx, python-pptx, Unstructured |
| Progress DB | SQLite (via db_manager.py) |

---

## Team

| Name | Contribution |
|---|---|
| Member 1 | RAG pipeline, vector store |
| Member 2 | Document processing, CS utils |
| Member 3 | Streamlit UI, components |
| Member 4 | Prompts, DB, deployment |

---

## Viva Talking Points

- **Multi-source RAG**: documents from different content types (textbooks vs past papers) are tagged and retrieved together, giving the LLM context from multiple perspectives.
- **Key rotation**: `APIKeyManager` cycles through multiple Groq keys automatically when rate limits hit — no manual intervention needed.
- **CS-specific analysis**: `track_a1_cs.py` detects programming languages, identifies algorithms, and estimates Big-O complexity from document content.
- **Three prompt modes**: Study, Exam, and Quick Revision use different prompt templates tuned for depth vs speed vs exam format.
- **SQLite progress DB**: schema covers topic mastery, session history, study plans, and extracted exam questions — ready to be wired to UI analytics.
