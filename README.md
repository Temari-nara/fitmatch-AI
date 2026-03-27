# FitMatch AI 🎯

**Smart Resume Analyzer & Job Fit Scorer** — Powered by Llama 3 on Groq

Upload your resume, enter a target job, and get an AI-powered fit score with actionable feedback.

---

## Quick Start (Local Setup)

### Step 1: Get a Free Groq API Key
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Go to **API Keys** and create a new key
4. Copy the key — you'll need it in Step 3

### Step 2: Clone and Install
```bash
git clone https://github.com/YOUR_USERNAME/AI-FIT-CHECK.git
cd AI-FIT-CHECK
pip install -r requirements.txt
```

### Step 3: Set Up Your API Key
```bash
# Copy the example env file
cp .env.example .env

# Open .env and replace 'your_groq_api_key_here' with your actual key
```

Your `.env` file should look like:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Run the App
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`

---

## How to Use
1. **Resume tab** — Upload a PDF or paste your resume text
2. **Job Target tab** — Paste a job description OR type a job title
3. **Results tab** — Click "Analyze Now" to get your fit score and feedback

---

## Deploy on Hugging Face Spaces (Free Hosting)

1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **Create new Space**
3. Choose **Streamlit** as the SDK
4. Upload all project files (or connect your GitHub repo)
5. Go to **Settings > Secrets** and add:
   - Name: `GROQ_API_KEY`
   - Value: your Groq API key
6. The app will build and deploy automatically!

---

## Tech Stack
| Component | Tool | Why |
|-----------|------|-----|
| Frontend | Streamlit | Simple Python UI, no HTML/CSS needed |
| LLM | Groq (Llama 3) | Free API, fast inference |
| PDF Parsing | PyMuPDF | Fast, no external dependencies |
| Env Vars | python-dotenv | Keeps API keys out of code |

---

## Project Structure
```
AI-FIT-CHECK/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── .env.example            # Template for API key
├── README.md               # This file
└── utils/
    ├── __init__.py         # Makes utils a Python package
    ├── resume_parser.py    # PDF text extraction
    ├── analyzer.py         # Groq API calls
    └── prompts.py          # LLM prompt templates
```

---

Built for the AI Workshop Demo 🚀
