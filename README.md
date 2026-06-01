<div align="center">

# 🧠 Smart AI Tutor

### A Self-Evolving Multi-Agent AI Education Platform

**using LangGraph · Google Gemini · RAG · Random Forest**

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-purple?style=flat-square)](https://langchain.com/langgraph)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-orange?style=flat-square&logo=google)](https://ai.google.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6.0-F7931E?style=flat-square&logo=scikit-learn)](https://scikit-learn.org)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-teal?style=flat-square)](https://trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> **M.Sc. AI & ML Major Project** — Mohd Anas (24MAM023) · Dept. of Computer Science · Jamia Millia Islamia

</div>

---

## 📌 What is Smart AI Tutor?

Smart AI Tutor is a **web-based intelligent tutoring system** that goes beyond simply answering student questions. Every question is processed through a **5-node LangGraph agent pipeline** before any answer is shown. Students can upload their own PDF textbooks and get answers grounded in those exact documents. A **Random Forest ML model** with 10 engineered features predicts each student's next quiz score.

**The core idea:** AI should not just answer questions — it should teach.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **5-Agent AI Pipeline** | LangGraph pipeline: Classify → Retrieve → Map → Generate → Check |
| 📖 **5 Teaching Modes** | Tutor, Socratic, Exam Prep, Creative, Debug — switch mid-session |
| 📄 **PDF Chat (RAG)** | Upload your textbook — AI answers from your actual course material |
| 📝 **Smart Quiz Engine** | AI-generated MCQs (Easy/Medium/Hard) with instant graded feedback |
| 🗺️ **Study Plan Generator** | 4-week AI roadmap with daily task breakdown |
| 🔮 **Score Predictor** | Random Forest ML model with 10 features — 45% better than linear regression |
| 📊 **Analytics Dashboard** | Chart.js score trends, subject heatmaps, improvement metrics |
| 📓 **Markdown Notes** | Subject-tagged notes with pin and full CRUD |
| 🏆 **Gamification** | XP, levels (1 per 500 XP), streaks, 20+ achievements, leaderboard |
| 🔐 **Secure Auth** | bcrypt passwords, JWT tokens, per-user data isolation |

---

## 📸 Screenshots

> **How to add your screenshots:**
> 1. Take screenshots of each page from your running app (`http://localhost:5000`)
> 2. Create a folder called `screenshots/` in the root of this project
> 3. Save each image there with the exact filename shown below
> 4. Push everything to GitHub — the images will appear automatically

---

### 🏠 Landing Page
<!-- Upload screenshot as: screenshots/landing.png -->
![Landing Page](screenshots/landing.png)

---

### 📊 Student Dashboard
<!-- Upload screenshot as: screenshots/dashboard.png -->
![Dashboard](screenshots/dashboard.png)

---

### 🤖 AI Tutor Chat — 5 Teaching Modes
<!-- Upload screenshot as: screenshots/tutor_chat.png -->
<!-- Tip: Show the Agent Pipeline sidebar open on the right -->
![AI Tutor Chat](screenshots/tutor_chat.png)

---

### 📝 Smart Quiz Engine
<!-- Upload screenshot as: screenshots/quiz.png -->
<!-- Tip: Capture a quiz in progress showing MCQ options and the timer -->
![Smart Quiz](screenshots/quiz.png)

---

### 📄 PDF Chat (RAG Mode)
<!-- Upload screenshot as: screenshots/pdf_chat.png -->
<!-- Tip: Show a PDF loaded on the left and an answer on the right -->
![PDF Chat](screenshots/pdf_chat.png)

---

### 🔮 Performance Predictor
<!-- Upload screenshot as: screenshots/predictor.png -->
<!-- Tip: Show predicted scores, mastery levels, and AI coaching -->
![Performance Predictor](screenshots/predictor.png)

---

### 📈 Analytics Dashboard
<!-- Upload screenshot as: screenshots/analytics.png -->
<!-- Tip: Show the score trend line chart and subject bar chart together -->
![Analytics](screenshots/analytics.png)

---

### 🗺️ Study Plans
<!-- Upload screenshot as: screenshots/study_plans.png -->
![Study Plans](screenshots/study_plans.png)

---

### 🏆 Leaderboard
<!-- Upload screenshot as: screenshots/leaderboard.png -->
![Leaderboard](screenshots/leaderboard.png)

---

### 👤 Student Registration — 3-Step Wizard
<!-- Upload screenshot as: screenshots/register.png -->
![Registration](screenshots/register.png)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│               PRESENTATION LAYER                                │
│   HTML5 / CSS3 / Vanilla JavaScript / Jinja2 / Chart.js        │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP + JSON (REST API)
┌──────────────────────────▼──────────────────────────────────────┐
│               APPLICATION LAYER  (Flask 3.x)                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           LangGraph 5-Node Agent Pipeline                │  │
│  │  [1] CLASSIFY → [2] RETRIEVE → [3] MAP →                │  │
│  │  [4] GENERATE (Gemini API) → [5] CHECK                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  QuizAgent · StudyPlanAgent · RAGEngine · RF Predictor         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│               DATA LAYER                                        │
│   SQLite + SQLAlchemy ORM  │  ChromaDB Vector Store (per-user) │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────▼───────────────┐
              │   Google Gemini 1.5 Flash  │
              │   (called only in Node 4)  │
              └────────────────────────────┘
```

---

## 🤖 The 5-Agent LangGraph Pipeline

Every student question passes through five agents before any answer appears:

| Node | Name | What It Does |
|---|---|---|
| 1 | **Classify** | Detects intent (`explain_concept`, `solve_problem`, `code_help`, etc.) and estimates complexity from student XP level |
| 2 | **Retrieve** | Fetches domain-specific knowledge + curated resources (Wolfram Alpha, Khan Academy, etc.) |
| 3 | **Map** | Identifies prerequisite concepts and suggests the next learning steps in the curriculum |
| 4 | **Generate** | Builds the full system prompt (mode + profile + history + RAG context) and calls Google Gemini |
| 5 | **Check** | Validates response quality, extracts follow-up questions, logs pipeline steps for UI sidebar |

> Only **Node 4** makes an external API call. All other nodes run locally in milliseconds.

---

## 🔮 Performance Predictor — Random Forest Model

The predictor trains on the student's own quiz history using a **sliding-window strategy**:

**10 Features per quiz attempt:**

```
last_score      → Most recent quiz score
last3_avg       → Average of last 3 scores  (short-term momentum)
all_avg         → Overall subject average   (long-term baseline)
trend           → (last − first) / (n−1)   (direction of change)
std_dev         → Score consistency
momentum        → last3_avg − all_avg
attempts        → Number of quizzes taken
days_since_last → Days since last quiz      (staleness)
difficulty_score→ easy=1 / medium=2 / hard=3
subject_id      → Numeric subject encoding  (0-9)
```

**Accuracy improvement over linear regression:**

| Metric | Linear Regression | Random Forest | Improvement |
|---|---|---|---|
| MAE  | ~14.2% | ~7.8%  | **45% better** |
| RMSE | ~17.6% | ~9.4%  | **47% better** |

Falls back to **EWMA (alpha=0.4)** for students with fewer than 3 quiz attempts.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or 3.11
- A free **Google Gemini API key** → [Get one here](https://aistudio.google.com/app/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/smart-ai-tutor.git
cd smart-ai-tutor
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=AIzaSy...your_key_here
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production
```

### 5. Run the application

```bash
python app.py
```

### 6. Open in browser

```
http://localhost:5000
```

> **No API key?** The app runs in demo mode — full UI, gamification, and 50+ fallback quiz questions still work without Gemini access.

---

## 📁 Project Structure

```
smart-ai-tutor/
│
├── app.py                          # Main Flask app, DB models, all routes
├── requirements.txt                # Python dependencies
├── setup.sh                        # Automated setup script (Mac/Linux)
├── HOW_TO_RUN.html                 # Step-by-step setup guide
├── .env.example                    # Environment variable template
├── .env                            # Your API keys (git-ignored)
│
├── backend/
│   ├── agents/
│   │   ├── tutor_agent.py          # LangGraph 5-node pipeline
│   │   ├── performance_predictor.py# Random Forest ML predictor
│   │   ├── rag_engine.py           # ChromaDB RAG (PDF chat)
│   │   ├── quiz_agent.py           # Quiz generation + evaluation
│   │   ├── study_plan_agent.py     # AI study plan generator
│   │   └── analytics_agent.py      # Analytics + achievement engine
│   └── routes/
│       ├── auth.py                 # Login, register, logout
│       ├── pages.py                # HTML page routes
│       └── api.py                  # REST API endpoints
│
├── frontend/
│   ├── templates/
│   │   ├── base.html               # Sidebar layout shell
│   │   ├── landing.html            # Public landing page
│   │   ├── performance.html        # RF predictor dashboard
│   │   ├── pdf_chat.html           # RAG document chat
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html       # 3-step registration wizard
│   │   └── pages/
│   │       ├── dashboard.html      # Student home
│   │       ├── tutor.html          # AI chat + agent steps sidebar
│   │       ├── quiz.html           # Adaptive quiz interface
│   │       ├── study_plans.html    # 4-week roadmap view
│   │       ├── analytics.html      # Chart.js visualizations
│   │       ├── notes.html          # Markdown notes editor
│   │       ├── leaderboard.html    # XP leaderboard
│   │       └── profile.html        # Achievements + history
│   └── static/
│       ├── css/
│       │   ├── main.css            # Dark editorial design system
│       │   └── theme.css           # Light/dark theme tokens
│       └── js/
│           ├── main.js             # Toast, Modal, API, XP utilities
│           └── theme.js            # Theme toggle
│
└── instance/
    ├── neurtutor.db                # SQLite database (auto-created)
    ├── chroma_db/                  # ChromaDB vector store (auto-created)
    └── uploads/                    # Student PDF uploads (auto-created)
```

---

## ⚙️ Environment Variables

```env
# ── REQUIRED ──────────────────────────────────────
GEMINI_API_KEY=AIzaSy...your_key_here       # Get free at aistudio.google.com
GEMINI_MODEL=gemini-1.5-flash               # Model to use

# ── SECURITY (change before deploying!) ───────────
SECRET_KEY=change-me-to-a-long-random-string
JWT_SECRET_KEY=change-me-to-another-random-string

# ── SERVER ────────────────────────────────────────
PORT=5000
HOST=0.0.0.0
FLASK_ENV=development

# ── DATABASE ──────────────────────────────────────
# Default: SQLite (no setup needed)
# For production: postgresql://user:password@localhost/dbname
```

---

## 🌐 API Reference

### Chat & Tutoring

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send message through 5-agent pipeline |
| `POST` | `/api/pdf/upload` | Upload PDF for RAG ingestion |
| `GET`  | `/api/pdf/documents` | List uploaded documents |
| `POST` | `/api/pdf/chat` | Chat grounded in uploaded PDF |

### Quiz

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/quiz/generate` | Generate AI quiz (subject, difficulty, count) |
| `POST` | `/api/quiz/submit` | Submit answers — returns score, grade, XP |

### Learning

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/study-plan/generate` | Generate 4-week study plan |
| `GET`  | `/api/analytics` | Performance analytics data |
| `GET`  | `/api/performance/predict` | RF predictor — predicted scores per subject |
| `GET`  | `/api/leaderboard` | Top-20 XP ranking |
| `GET/POST/PUT/DELETE` | `/api/notes` | Notes CRUD |
| `GET`  | `/api/user/stats` | XP, level, streak, achievements |

### Sample Response — `/api/chat`

```json
{
  "response": "**Newton's Second Law** — F = ma ...",
  "agent_steps": [
    "✅ Intent: explain_concept | Complexity: Basic",
    "✅ Knowledge retrieved for Physics",
    "✅ Curriculum mapped: prerequisites identified",
    "✅ Gemini 1.5 Flash generated Tutor response",
    "✅ Quality checked"
  ],
  "resources": [{"type": "tool", "name": "PhET Simulations", "url": "https://phet.colorado.edu"}],
  "xp_earned": 10,
  "total_xp": 1260,
  "level": 3,
  "new_achievements": [],
  "rag_used": false
}
```

---

## 🗃️ Database Schema

```
users            — credentials, grade, style, XP, level, streak, subjects
learning_sessions— conversation JSON, agent mode, XP earned, started_at
quiz_results     — subject, difficulty, score (%), grade, taken_at
achievements     — key, title, icon, xp_value, earned_at
study_plans      — subject, goal, plan JSON, deadline, progress
notes            — subject, content (Markdown), is_pinned, tags
```

**XP and Level formula:**
```
level   = 1 + (xp_points // 500)
progress = (xp_points % 500) / 500 × 100%
```

---

## 🏆 Gamification

| Action | XP Earned |
|---|---|
| Sending a chat message | +10 XP |
| Completing a quiz | max(5, score × 2) XP |
| Getting 100% on a quiz | +200 XP (once) |
| Creating an account | +100 XP |
| Achievement unlocked | +50 to +500 XP |

**Selected Achievements:**

| Achievement | Trigger | XP |
|---|---|---|
| 🌟 Welcome Scholar | Register account | 100 |
| 💬 First Question | Ask first question | 50 |
| 💯 Perfect Score | Get 100% on any quiz | 200 |
| 📝 Quiz Veteran | Complete 20 quizzes | 300 |
| 🔥 Week Warrior | 7-day study streak | 250 |
| 🏅 Monthly Master | 30-day streak | 500 |
| 🌍 Polymath | Study 3+ subjects | 200 |

---

## 🛠️ Technologies

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11 | Backend language |
| Flask | 3.x | Web framework + routing |
| LangGraph | 0.1.x | 5-node multi-agent pipeline |
| LangChain (Google) | 0.2.x | Gemini API wrapper |
| Google Gemini | 1.5 Flash | LLM for tutoring, quizzes, plans |
| **scikit-learn** | **1.6.0** | **Random Forest score predictor** |
| ChromaDB | 0.5.x | Per-user PDF vector storage |
| SQLAlchemy | 2.x | ORM — no raw SQL |
| SQLite | — | Database (PostgreSQL-ready) |
| Flask-Login + JWT | — | Auth + API tokens |
| Flask-Bcrypt | — | bcrypt password hashing |
| PyMuPDF + PyPDF2 | — | PDF text extraction |
| Chart.js | 4.4.0 | Analytics charts |
| python-dotenv | — | Environment config |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Activate venv then `pip install -r requirements.txt` |
| Gemini API error | Check `GEMINI_API_KEY` in `.env` — get one free at [aistudio.google.com](https://aistudio.google.com) |
| Shows "Demo Mode" | Add a real `GEMINI_API_KEY` to `.env` |
| Port 5000 in use | Set `PORT=5001` in `.env` |
| Database error | Delete `instance/neurtutor.db` and restart — it recreates automatically |
| PDF chat not working | Check `instance/chroma_db/` exists and is writable |
| Score shows 1000%+ | Update `performance_predictor.py` — the `score` field is already a percentage |

---

## 🚀 Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:5000

# With PostgreSQL (recommended for production)
pip install psycopg2-binary
# Set in .env:
# DATABASE_URL=postgresql://user:password@localhost/smart_ai_tutor
```

---

## 📄 Academic Context

This project was developed as a **Major Project** for:

- **Programme:** M.Sc. Artificial Intelligence & Machine Learning — Semester IV
- **Department:** Computer Science, Faculty of Sciences
- **Institution:** Jamia Millia Islamia (A Central University), New Delhi – 110025
- **Supervisor:** Prof. Jahiruddin
- **Student:** Mohd Anas — Roll No: 24MAM023 — Enrollment: 24-05264
- **Session:** 2025–2026

**Key academic contributions:**

- ✅ Multi-agent AI architecture using LangGraph (not a single LLM call)
- ✅ Per-user Retrieval-Augmented Generation with ChromaDB isolation
- ✅ Machine learning performance prediction (Random Forest, 10 features, 45% better MAE)
- ✅ Full gamification loop with immediate reward delivery
- ✅ 8 real bugs found, diagnosed, and resolved during development

---

## 📜 References

1. Bloom, B. S. (1984). The 2 Sigma Problem. *Educational Researcher*.
2. Lewis et al. (2020). Retrieval-Augmented Generation. *NeurIPS*.
3. Breiman, L. (2001). Random Forests. *Machine Learning*.
4. Pedregosa et al. (2011). Scikit-learn. *JMLR*.
5. Hamari et al. (2014). Does Gamification Work? *HICSS*.
6. LangChain AI. (2024). *LangGraph Documentation*. https://langchain.com/langgraph

---

<div align="center">

**Made with ❤️ for students — by a student**

*Smart AI Tutor — Jamia Millia Islamia — May 2026*

</div>
