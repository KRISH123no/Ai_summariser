# Ai_summariser
# 📚 AI Summarizer — StudyAI

A locally hosted AI-powered study tool built with Python and Flask. Upload any PDF or paste a YouTube link and instantly generate study materials — no internet, no API costs, runs entirely on your machine.

---

## ✨ Features

- **PDF Upload** — Extract and analyze content from any PDF document
- **YouTube Support** — Paste any YouTube URL with captions to generate study materials
- **6 Study Tools** — Choose what you need:
  - 📝 Summary — Clean 200-300 word overview
  - 📒 Notes — Structured notes with headings and bullet points
  - ❓ Quiz — 10 interactive multiple choice questions with instant feedback
  - 🃏 Flashcards — 15 flippable flashcards with Previous/Next navigation
  - 📊 PPT Outline — 8-10 slide presentation outline
  - 🔍 Key Concepts — Glossary of 10-15 key terms with definitions

---

## 🛠️ Tech Stack

- **Backend** — Python, Flask
- **AI** — Ollama (local LLM), Mistral 7B
- **PDF Processing** — PyPDF2
- **YouTube** — youtube-transcript-api
- **Frontend** — HTML, CSS, JavaScript (Cyberpunk dark theme)

---

## 🚀 How to Run

**1. Install Ollama and pull the model:**
```bash
brew install ollama
ollama pull mistral
```

**2. Install dependencies:**
```bash
pip3 install flask requests PyPDF2 youtube-transcript-api
```

**3. Start Ollama in one terminal:**
```bash
ollama serve
```

**4. Run the app in another terminal:**
```bash
cd ai_summarizer
python3 app.py
```

**5. Open browser:**
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
ai_summarizer/
├── app.py                  # Flask backend and routes
├── templates/
│   ├── index.html          # Main input page
│   └── result.html         # Results page with tabs
└── static/
    ├── style.css           # Cyberpunk dark UI theme
    └── script.js           # Frontend interactions
```

---

## 📌 Notes

- Works best with PDFs under 5 pages
- YouTube videos must have captions enabled
- First generation takes ~30 seconds to load the model, faster after that
- Selecting multiple features at once increases processing time

---

Built with Python and Flask
