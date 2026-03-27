---
title: FitMatch AI
emoji: 🎯
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.44.1"
app_file: app.py
pinned: false
short_description: AI Resume Analyzer & Job Fit Scorer
---

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
git clone https://github.com/Temari-nara/fitmatch-AI.git
cd fitmatch-AI
pip install -r requirements.txt
```

### Step 3: Set Up Your API Key
```bash
cp .env.example .env
# Open .env and replace 'your_groq_api_key_here' with your actual key
```

### Step 4: Run the App
```bash
streamlit run app.py
```

---

## How to Use
1. **Resume tab** — Upload a PDF or paste your resume text
2. **Job Target tab** — Paste a job description OR type a job title
3. **Results tab** — Click "Analyze Now" to get your fit score and feedback

---

## Tech Stack
| Component | Tool | Why |
|-----------|------|-----|
| Frontend | Streamlit | Simple Python UI, no HTML/CSS needed |
| LLM | Groq (Llama 3) | Free API, fast inference |
| PDF Parsing | PyMuPDF | Fast, no external dependencies |
| Env Vars | python-dotenv | Keeps API keys out of code |

---

Built for the AI Workshop Demo 🚀
