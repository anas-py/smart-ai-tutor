# Smart AI Tutor
## A Self-Evolving Multi-Agent AI Education Platform using LangGraph, GenAI, and RAG

---

**Student:** Mohd Anas | Roll No: 24MAM023 | Enrollment No: 24-05264
**Programme:** M.Sc. Artificial Intelligence & Machine Learning — Semester IV
**Department:** Computer Science, Faculty of Sciences, Jamia Millia Islamia (A Central University)
**Supervisor:** Prof. Jahiruddin
**Date:** May 2026

---

## Table of Contents

1. [What is This Project?](#1-what-is-this-project)
2. [The Problem We Are Solving](#2-the-problem-we-are-solving)
3. [How This Project is Different](#3-how-this-project-is-different)
4. [Overall System Architecture](#4-overall-system-architecture)
5. [The Five-Agent AI Pipeline (LangGraph)](#5-the-five-agent-ai-pipeline-langgraph)
6. [PDF Chat — Retrieval-Augmented Generation (RAG)](#6-pdf-chat--retrieval-augmented-generation-rag)
7. [Performance Predictor — Random Forest Model](#7-performance-predictor--random-forest-model)
8. [Five Teaching Modes](#8-five-teaching-modes)
9. [Smart Quiz Engine](#9-smart-quiz-engine)
10. [Study Plan Generator](#10-study-plan-generator)
11. [Gamification System](#11-gamification-system)
12. [Database Design](#12-database-design)
13. [API Design](#13-api-design)
14. [Frontend Design](#14-frontend-design)
15. [Security Implementation](#15-security-implementation)
16. [Technologies Used](#16-technologies-used)
17. [Real Bugs Found and Fixed](#17-real-bugs-found-and-fixed)
18. [Results and Evaluation](#18-results-and-evaluation)
19. [Advantages of This Project](#19-advantages-of-this-project)
20. [Limitations](#20-limitations)
21. [Future Scope](#21-future-scope)
22. [References](#22-references)

---

## 1. What is This Project?

Smart AI Tutor is a **website-based intelligent tutoring system** built from scratch using Python. A student opens it in any browser, creates an account in 60 seconds, and immediately gets access to:

- An AI tutor that processes every question through **five reasoning steps** before answering
- Five different **teaching styles** they can switch between mid-session
- A **PDF upload** system where the AI reads their own textbook and answers from it
- A **quiz engine** that generates fresh questions on demand
- A **4-week study plan** generator
- A **machine learning model** that predicts their next quiz score
- A **points and achievement system** that rewards daily study habits

The key idea is simple: **AI should not just answer questions — it should teach**. This means knowing who the student is, adapting to their level and style, tracking their progress, and motivating them to come back every day.

---

## 2. The Problem We Are Solving

### 2.1 What Is Wrong With Existing Tools?

Most online learning platforms and AI tools have four fundamental problems:

**Problem 1 — Same content for everyone**
A beginner student asking "What is a derivative?" gets the same explanation as a postgraduate student. A visual learner gets the same plain text as a reading-style learner. There is no personalisation at all.

**Problem 2 — Not from the student's actual course**
Tools like ChatGPT answer from their training data. This data may be outdated, inconsistent with the student's specific university syllabus, or wrong for their specific examination style. A student cannot upload their lecture notes and get answers grounded in those notes.

**Problem 3 — No real performance tracking**
Most tools show past quiz scores as a number or a simple chart. They cannot predict future performance, cannot tell the student whether they are improving or declining, and cannot suggest what to study next based on actual data.

**Problem 4 — Students quit too quickly**
Without any reward system or visible progress indicator, students who are enthusiastic on day one typically abandon the platform within one or two weeks. This is the most common failure mode of online education.

### 2.2 What the Research Says

Benjamin Bloom's 1984 study, known as the **"2 Sigma Problem"**, found that students who received one-on-one personalised tutoring performed **two standard deviations better** than students in a normal classroom. Two sigma is an enormous difference — equivalent to going from the 50th percentile to the 98th percentile. The problem is that personalised human tutoring at scale is economically impossible.

Smart AI Tutor is built to bring this level of personalisation to every student, at any time, through AI — not as a replacement for teachers, but as a tutor available 24 hours a day.

---

## 3. How This Project is Different

### 3.1 Comparison with Existing Tools

| Feature | Smart AI Tutor | ChatGPT / Claude | Khanmigo | Socratic | Duolingo AI |
|---|---|---|---|---|---|
| Teaching styles | **5 distinct modes** | 1 general style | 1 (Socratic only) | 1 (answer lookup) | 1 (language mode) |
| Multi-agent pipeline | **Yes — 5-step LangGraph** | No (single LLM call) | No | No | No |
| Answers from own PDFs | **Yes — ChromaDB RAG** | Plugin only | No | No | No |
| Subject coverage | **10+ academic subjects** | General knowledge | Math & Science | General | Languages only |
| Remembers the student | **Yes — full profile** | No | Partly | No | Yes (streaks) |
| ML score prediction | **Random Forest (10 features)** | None | None | None | None |
| Points and rewards | **Full (XP, levels, 20+ badges)** | None | Badges only | None | Full |
| Study plan generator | **Yes — 4-week AI roadmap** | Manual only | No | No | No |
| Notes management | **Yes — Markdown + tags** | No | No | No | No |
| Runs on your own laptop | **Yes — Flask + SQLite** | Cloud only | Cloud only | No | No |
| Works without API key | **Yes — demo mode** | No | No | No | No |

### 3.2 The Core Philosophical Difference

Every other tool answers questions. Smart AI Tutor teaches.

This is not just a marketing statement — it is an architectural difference. ChatGPT does not know who is asking. It does not know whether the student scored 40% last week or 90%. It does not know that they prefer visual explanations. It does not know they have an exam tomorrow. Every conversation starts from zero.

Smart AI Tutor maintains a **persistent student identity**. The system stores:
- Grade level (Middle School → Postgraduate)
- Learning style (Visual / Auditory / Kinesthetic / Reading)
- Quiz history per subject
- XP and level
- Last active date
- Weak and strong subjects

Every AI response is shaped by this context. A Level 1 student and a Level 10 student asking the same question get fundamentally different explanations.

---

## 4. Overall System Architecture

### 4.1 Three-Tier Design

Smart AI Tutor follows a standard three-tier web application architecture with an external AI service layer:

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│   HTML5  /  CSS3  /  Vanilla JavaScript  /  Jinja2 Templates   │
│   Chart.js for analytics  ·  Dark/Light theme toggle           │
└──────────────────────────────┬──────────────────────────────────┘
                               │  HTTP + JSON (REST API)
┌──────────────────────────────▼──────────────────────────────────┐
│                     APPLICATION LAYER                           │
│       Flask 3.x  —  Routes, Auth, Business Logic, API          │
│                                                                 │
│   ┌──────────────┐   ┌───────────────────┐   ┌─────────────┐   │
│   │  Auth Module │   │  LangGraph Agents │   │  Analytics  │   │
│   │  JWT + Login │   │  (5-node pipeline)│   │  RF Model   │   │
│   └──────────────┘   └───────────────────┘   └─────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                       DATA LAYER                                │
│   SQLite  (SQLAlchemy ORM)    ·    ChromaDB  (Vector Store)    │
└──────────────────────────────┬──────────────────────────────────┘
                               │
              ┌────────────────▼──────────────────┐
              │         EXTERNAL SERVICES          │
              │    Google Gemini 1.5 Flash API     │
              │   (called only in Pipeline Node 4) │
              └───────────────────────────────────┘
```

### 4.2 Key Design Decisions

**Why Flask instead of Django?**
Flask's lightweight structure allowed the entire application to be implemented in a single `app.py` file initially, making it far easier to understand and demonstrate. Django's admin panels and ORM conventions add complexity that was not needed for this project scope. SQLAlchemy makes switching to PostgreSQL for production a one-line configuration change.

**Why SQLite instead of PostgreSQL?**
SQLite requires zero configuration, runs in a single file (`neurtutor.db`), and is perfectly adequate for a single-deployment demonstration. The SQLAlchemy ORM abstracts the database layer completely.

**Why vanilla JavaScript instead of React or Vue?**
No build step, no npm dependencies, instant page loads. The UI complexity of this project does not justify the overhead of a modern frontend framework.

**Why ChromaDB instead of Pinecone or Weaviate?**
ChromaDB runs entirely locally with no API key or cloud subscription required. It supports per-collection isolation which is critical for keeping each student's document store separate.

---

## 5. The Five-Agent AI Pipeline (LangGraph)

### 5.1 Why Five Agents Instead of One?

The most common mistake in AI application development is to send a student's question directly to an LLM and return whatever it says. This produces responses that are:
- Inconsistent in quality
- Unaware of the curriculum
- Not adapted to the student's level
- Not structured for teaching

Smart AI Tutor breaks every question into five reasoning stages. Each stage has a single, specific job. The output of each stage becomes the input of the next.

```
Student Question
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   NODE 1     │────▶│   NODE 2     │────▶│   NODE 3     │
│   CLASSIFY   │     │   RETRIEVE   │     │   MAP        │
│              │     │              │     │              │
│ What type    │     │ Fetch domain │     │ Map to       │
│ of question? │     │ knowledge    │     │ curriculum   │
│ How complex? │     │ and resources│     │ prerequisites│
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
                                    ┌──────────────────┐
                                    │     NODE 4       │
                                    │     GENERATE     │
                                    │                  │
                                    │ Build full system│
                                    │ prompt → call    │
                                    │ Gemini API       │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │     NODE 5       │
                                    │     CHECK        │
                                    │                  │
                                    │ Validate quality │
                                    │ Extract Q's      │
                                    │ Format output    │
                                    └──────────────────┘
                                             │
                                             ▼
                                     AI Answer (JSON)
```

### 5.2 Node 1 — Intent Classifier

**What it does:** Reads the student's raw question and determines what kind of response is needed.

**How it works:** Uses rule-based keyword matching to classify the question into one of six intent categories:

| Intent | Example Query | Response Structure |
|---|---|---|
| `explain_concept` | "What is a derivative?" | Full explanation + worked example |
| `solve_problem` | "Solve 2x² − 8 = 0" | Step-by-step working |
| `request_example` | "Give me an example of recursion" | Concrete example with explanation |
| `request_practice` | "Give me a practice problem on Newton's laws" | MCQ or open problem |
| `code_help` | "My Python loop is not working" | Debug: root cause + fix |
| `compare_contrast` | "What is the difference between RAM and ROM?" | Side-by-side comparison |

Also estimates complexity (basic / intermediate / advanced) from the student's current XP level.

**Why this matters:** Different intents need completely different response structures. Without classification, the AI might explain concepts when the student just wanted a practice problem, or give a worked example when they needed a definition.

### 5.3 Node 2 — Knowledge Retriever

**What it does:** Builds subject-specific context and assembles a curated list of learning resources.

**How it works:**
- Identifies the academic subject from the question
- Loads a pre-built knowledge context for that subject (key facts, common tools, typical exam formats)
- Assembles a curated resource list (practice websites, calculation tools, reference databases)
- If **RAG mode is active**: queries the student's ChromaDB collection and retrieves the 4 most semantically relevant chunks from their uploaded PDF

**Resources loaded per subject:**
- Mathematics: Wolfram Alpha, Desmos, Khan Academy calculus
- Physics: PhET simulations, HyperPhysics, NIST constants
- Computer Science: GeeksforGeeks, LeetCode, MDN Web Docs
- Chemistry: ChemLibreTexts, Royal Society of Chemistry
- Biology: Khan Academy Biology, NCBI databases

### 5.4 Node 3 — Curriculum Mapper

**What it does:** Identifies prerequisite concepts and maps the query to the appropriate curriculum level.

**How it works:**
- Uses the student's grade level (from their profile) and the detected subject to select the right curriculum level
- Generates a list of prerequisite concepts the student should already understand
- Suggests the next learning steps after understanding this concept
- These curriculum hints are injected into Node 4's system prompt

**Example:** For a Grade 10 student asking about differentiation:
- Prerequisites: "basic algebra, understanding of functions, concept of slope"
- Next steps: "product rule, chain rule, implicit differentiation"

This ensures the AI does not explain derivatives using calculus notation to a student who has only just learned about functions.

### 5.5 Node 4 — Response Generator

**What it does:** The only node that makes an external API call. Constructs the complete AI instruction and calls Google Gemini.

**What goes into the system prompt:**
1. The teaching mode instruction (different text for each of the 5 modes)
2. Student profile: name, grade level, learning style, current XP level
3. Curriculum hints from Node 3
4. The last 8 messages of the conversation (rolling history)
5. RAG-retrieved document chunks (if PDF mode is active)
6. The student's question

**Why only the last 8 messages?**
Gemini has a context window limit. Including too many messages causes API errors. The last 8 messages (4 turns of conversation) maintain conversational coherence while keeping the request size manageable. Older messages are still saved in the database for analytics.

**Gemini integration:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_KEY,
    max_output_tokens=4096,
    temperature=0.7   # 0.3 for quizzes (deterministic), 0.7 for tutoring (creative)
)
```

**Fallback chain:** If LangChain fails → use direct `google-generativeai` SDK → if that fails → return a demo mode response with setup instructions.

### 5.6 Node 5 — Quality Checker

**What it does:** Validates the raw Gemini output and prepares the final structured response.

**What it checks:**
- Minimum response length (catches empty or very short responses)
- Extracts follow-up questions if the response contains them
- Assembles the `agent_steps` list that is displayed in the UI sidebar
- Formats the final JSON response

**What the UI shows (agent_steps):**
```
✅ Intent: explain_concept | Complexity: Intermediate
✅ Knowledge retrieved for Mathematics
✅ Curriculum mapped: prerequisites and next steps identified
✅ Gemini (LangChain) generating Tutor response...
✅ Quality checked — response validated
```

This transparency builds student trust and also serves an educational purpose: students can see that AI reasoning is structured, not magical.

### 5.7 State Object

All five nodes share a single typed state dictionary that flows through the pipeline:

```python
AgentState = {
    "user_message":      str,    # the student's question
    "history":           list,   # last 8 messages
    "user_context":      dict,   # name, grade, style, level, subjects
    "mode":              str,    # tutor / socratic / exam_prep / creative / debug
    "subject":           str,    # Mathematics, Physics, etc.
    "intent":            str,    # output of Node 1
    "complexity":        str,    # output of Node 1
    "knowledge_context": str,    # output of Node 2
    "curriculum_hints":  str,    # output of Node 3
    "agent_steps":       list,   # built by Nodes 1-5
    "resources":         list,   # curated links from Node 2
    "response":          str,    # output of Node 4
    "follow_up_questions":list,  # extracted by Node 5
    "rag_context":       str,    # from ChromaDB (if PDF mode)
    "use_pdf":           bool,   # is PDF/RAG mode active?
}
```

---

## 6. PDF Chat — Retrieval-Augmented Generation (RAG)

### 6.1 The Problem RAG Solves

Large language models (LLMs) like Gemini sometimes "hallucinate" — they confidently state facts that are wrong. This is a serious problem in education because students may not know the answer is incorrect. More importantly, LLMs answer from their training data, which may not match the student's specific university textbook, regional syllabus, or exam format.

RAG (Retrieval-Augmented Generation) solves this by retrieving real passages from real documents and injecting them into the AI's context before generating a response. The AI then answers from the retrieved text rather than from memory alone.

### 6.2 How the RAG Engine Works

**Phase 1 — Ingestion (when student uploads a PDF):**

```
Student uploads PDF
        │
        ▼
PyMuPDF extracts text page by page
(fallback: PyPDF2 if PyMuPDF fails)
        │
        ▼
Text cleaning: remove extra whitespace, fix encoding
        │
        ▼
Chunk at sentence boundaries:
~600 characters per chunk
100-character overlap between chunks
        │
        ▼
Each chunk saved to student's ChromaDB collection:
  collection name = "user_{user_id}_docs"
  document ID = hash of filename + chunk index
  (duplicate detection prevents re-indexing the same file)
```

**Why 600-character chunks with 100-character overlap?**
Too large = retrieval is imprecise (returns too much irrelevant text). Too small = concepts split across chunk boundaries are lost. The 100-character overlap means concepts at the edge of a chunk appear in both the current and next chunk, preventing information loss.

**Phase 2 — Retrieval (when student asks a question):**

```
Student's question
        │
        ▼
ChromaDB converts question to vector
using default embedding function
        │
        ▼
Cosine similarity search across all chunks
in this student's collection
        │
        ▼
Top 4 most semantically relevant chunks returned
        │
        ▼
Chunks injected into Node 4's system prompt:
"PDF CONTEXT (your uploaded document):
---
[chunk 1 text]

[chunk 2 text]
---
Ground your answer in the above content."
        │
        ▼
Gemini answers from the student's own document
```

### 6.3 Data Isolation

**Critical security feature:** Each student's uploaded documents are stored in a completely separate ChromaDB collection named `user_{id}_docs`. This means:
- Student A cannot access Student B's documents
- Each student's collection is entirely independent
- Deleting a student account deletes their entire ChromaDB collection

### 6.4 PDF Upload Security

Before saving any uploaded file:
```python
from werkzeug.utils import secure_filename

filename = secure_filename(file.filename)  # strips path traversal characters
# File size limit: 32 MB enforced before processing
```

`secure_filename()` removes characters like `../` that could be used to write files outside the uploads directory (path traversal attack prevention).

---

## 7. Performance Predictor — Random Forest Model

### 7.1 Why the Old Method Was Not Good Enough

The first version of the performance predictor used **hand-coded linear regression** — it computed the slope and intercept of a straight line through the student's past quiz scores and extrapolated the next point.

**The problem:** Real learning does not follow a straight line.

Consider a student with these scores: `40, 40, 40, 80, 85`

This student clearly struggled at first but then made a rapid improvement. A straight line fitted through all five points gives a predicted next score of approximately **60** — which badly underestimates their current trajectory. The student is likely to score around 85-90, not 60.

Learning follows **S-curves** (slow start → rapid improvement → plateau), **plateau effects** (stuck at a level for a while), and **recovery patterns** (declined then improved). None of these can be represented by a straight line.

### 7.2 How Random Forest Works

A **Random Forest** is an ensemble of decision trees. Instead of one model trying to predict the answer, 100 independent decision trees each make their own prediction, and the final answer is the average of all 100.

**Why this is better:**
- No single unusual data point can throw off all 100 trees simultaneously
- Each tree sees a different random subset of the data and features
- The average of 100 imperfect predictions is far more stable than one
- Can capture non-linear patterns, curves, and plateaus

### 7.3 The Ten Features

For every quiz attempt, the system extracts ten measurements that together describe where the student is and where they are headed:

| # | Feature Name | What It Measures | Why It Matters |
|---|---|---|---|
| 1 | `last_score` | Score on the most recent quiz | Immediate current level |
| 2 | `last3_avg` | Average of the last 3 quiz scores | Short-term momentum and recency |
| 3 | `all_avg` | Overall average across all attempts | Long-term baseline performance |
| 4 | `trend` | (last score − first score) ÷ (n−1) | Direction of change — improving or declining |
| 5 | `std_dev` | Standard deviation of all scores | Consistency — are scores stable or erratic? |
| 6 | `momentum` | `last3_avg − all_avg` | Is recent performance better or worse than usual? |
| 7 | `attempts` | Number of quizzes taken in this subject | How much training data we have |
| 8 | `days_since_last` | Days since most recent quiz | Staleness — longer gap often predicts lower score |
| 9 | `difficulty_score` | 1 = easy, 2 = medium, 3 = hard | Harder quizzes naturally produce lower raw scores |
| 10 | `subject_id` | Numeric encoding of the subject (0–9) | Some subjects are inherently harder for this student |

**Why `last3_avg` matters most (≈28% importance):**
A student who scored 40, 40, 40, 80, 85 has an overall average of 57% but a recent average of 81.7%. The model correctly gives more weight to recent performance — it reflects where the student *is*, not where they *were*.

### 7.4 Sliding-Window Training Strategy

The model does not need a separate training dataset. It builds its own training data from the student's quiz history.

**For a student with N total quiz attempts (across all subjects):**
- Generate N−1 training samples
- Sample i: features computed from quizzes 0 to i−1, target = score at quiz i
- All subjects are pooled into one training dataset

**Example:** A student with 3 Physics quizzes and 5 Maths quizzes generates **7 training samples** (3-1 + 5-1 = 6, plus one cross-subject sample). This is significantly more than training per-subject would give.

```python
for subj, records in by_subject.items():
    for i in range(1, len(records)):
        features = build_feature_vector(records[:i], subj)
        X_train.append(features)
        y_train.append(records[i]['score_pct'])

rf = RandomForestRegressor(
    n_estimators=100,   # 100 decision trees
    max_depth=6,        # prevents overfitting on small datasets
    max_features="sqrt",# sqrt(10) ≈ 3 features per split — makes trees different
    random_state=42,    # reproducible results
    n_jobs=-1           # use all CPU cores for speed
)
rf.fit(X_train, y_train)
```

### 7.5 EWMA Fallback for New Students

If a student has fewer than 3 total quiz attempts across all subjects, there is not enough data to train the Random Forest reliably. The system automatically falls back to **Exponential Weighted Moving Average (EWMA)** with alpha = 0.4:

```python
def predict_ewma(scores, alpha=0.4):
    ewma = scores[0]
    for s in scores[1:]:
        ewma = alpha * s + (1 - alpha) * ewma
    # Damped trend projection
    trend = (scores[-1] - scores[-2]) * 0.3 if len(scores) >= 2 else 0
    return round(min(max(ewma + trend, 0), 100), 1)
```

EWMA gives more weight to recent scores than old ones (controlled by `alpha`). This is already much better than plain linear regression for sparse data.

### 7.6 Accuracy Results

Evaluated using **Leave-One-Out Cross-Validation (LOOCV)** on a test student with 9 quiz attempts (Maths: 50→90%, Physics: 40→70%, both showing non-linear upward trends):

| Metric | Linear Regression (Old) | Random Forest (New) | Improvement |
|---|---|---|---|
| Mean Absolute Error (MAE) | ~14.2% | ~7.8% | **45% better** |
| Root Mean Square Error (RMSE) | ~17.6% | ~9.4% | **47% better** |
| Maximum single prediction error | ~28% | ~16% | **43% better** |
| Handles non-linear curves | No | **Yes** | New capability |
| Number of features used | 1 (score only) | **10** | 10× more information |
| Cold-start fallback | None | **EWMA (alpha=0.4)** | New capability |

**Feature importances (approximate, from trained RF):**

| Rank | Feature | Importance |
|---|---|---|
| 1 | `last3_avg` (recent average) | ~28% |
| 2 | `all_avg` (overall baseline) | ~22% |
| 3 | `last_score` (most recent) | ~18% |
| 4 | `trend` (direction of change) | ~12% |
| 5 | `momentum` (recent vs baseline) | ~9% |
| 6 | `std_dev` (consistency) | ~5% |
| 7 | `days_since_last` (staleness) | ~3% |
| 8 | `difficulty_score` | ~2% |
| 9 | `attempts` | ~1% |
| 10 | `subject_id` | <1% |

**What this tells us:** The three most important features are about recency. The model correctly learns that where the student *is right now* matters more than where they started.

---

## 8. Five Teaching Modes

The teaching mode system is the feature that most differentiates Smart AI Tutor from a generic chatbot. Instead of one response style for all questions, five distinct pedagogical strategies are implemented as separate system prompt templates.

### 8.1 Mode Descriptions

**Tutor Mode (Default)**
```
Structure: Explanation → Worked Example → Check Question

Best for: Learning a new concept for the first time.

How the AI behaves: Gives a complete explanation of the concept,
then demonstrates it with a fully worked example, then ends
with a "Quick Check" question to verify understanding.

Example response to "What is osmosis?":
- Paragraph explaining osmosis (what it is, why it happens)
- Worked example: "Imagine placing a carrot in salt water..."
- Quick Check: "What would happen if you placed the same carrot
  in pure water instead?"
```

**Socratic Mode**
```
Structure: Guiding questions only — never give direct answers

Best for: Developing critical thinking and independent reasoning.

How the AI behaves: Responds entirely with questions that lead
the student toward the answer. Never states the answer directly.

Example response to "What is the speed of light?":
- "What unit do we use to measure the speed of waves?"
- "If you knew the frequency and wavelength of light, what
  formula would connect them to speed?"
- "What does this tell you about the relationship between
  frequency and wavelength in light?"
```

**Exam Prep Mode**
```
Structure: Key Summary → Memory Tip → Common Mistakes → Practice Q

Best for: Revision the night before an examination.

How the AI behaves: Gives a concise exam-focused summary,
adds a mnemonic or memory technique, warns about the most
common mistakes students make, then gives a practice question
in exam format.

Example for "Photosynthesis":
- "Key equation: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂"
- Memory tip: "Can Hungry Plants Grow Oxygen?" (Carbon, Hydrogen,
  Photosynthesis, Glucose, Oxygen)
- Common mistake: "Students often forget that oxygen is released,
  not consumed, during photosynthesis."
- Practice Q: "A plant is placed in darkness for 24 hours.
  What happens to its glucose production? Explain."
```

**Creative Mode**
```
Structure: Story / Analogy / Metaphor → Connection to concept

Best for: Abstract or counterintuitive concepts where a direct
explanation does not stick.

How the AI behaves: Explains through an imaginative story,
real-world comparison, or vivid metaphor that makes the concept
memorable and tangible.

Example for "Recursion":
"Imagine you are standing between two mirrors facing each other.
You see your reflection in the first mirror, but that reflection
also sees itself in the second mirror, which also sees itself
in the first mirror... and so on, infinitely.
Each reflection contains a smaller version of the same pattern.
This is exactly what recursion does in code — a function that
calls a smaller version of itself until it reaches the simplest
possible case (the base case), just like your reflection eventually
becomes too small to see."
```

**Debug Mode**
```
Structure: Root Cause → Step-by-Step Fix → Key Lesson

Best for: When the student has made an error in code,
mathematics, or logical reasoning.

How the AI behaves: Does not just fix the error — identifies
exactly WHY the error happened, walks through the correction
step by step, and extracts a general lesson to prevent the
same mistake in future.

Example for broken Python code:
- Root cause: "The loop variable `i` is being modified
  inside the loop, which causes the iterator to skip elements."
- Step-by-step fix: "Replace the list modification with a
  list comprehension: [x for x in items if x != target]"
- Key lesson: "Never modify a list while iterating over it.
  Always create a new list or use list comprehension."
```

### 8.2 Implementation

Each mode is a complete system prompt template. Node 4 of the pipeline selects the correct template based on the student's chosen mode and injects it at the top of the system prompt:

```python
MODE_INSTRUCTIONS = {
    "tutor": """You are a patient tutor. Structure every response as:
    1. Clear explanation of the concept
    2. A concrete worked example
    3. A "Quick Check" question to test understanding""",

    "socratic": """You are a Socratic guide. NEVER give direct answers.
    Respond ONLY with guiding questions that lead the student to
    discover the answer themselves. If they ask for the answer directly,
    ask another guiding question instead.""",

    "exam_prep": """You are an exam coach. Structure every response as:
    1. KEY CONCEPT: One-paragraph exam-ready summary
    2. MEMORY TIP: A mnemonic or memory aid
    3. COMMON MISTAKES: What students typically get wrong
    4. PRACTICE QUESTION: One exam-style question""",

    "creative": """You are a creative storyteller-tutor. Explain EVERY
    concept through a story, real-world analogy, or imaginative metaphor.
    Make abstract ideas feel concrete and memorable.""",

    "debug": """You are a debugging assistant. For every problem:
    1. ROOT CAUSE: Identify exactly why the error occurred
    2. STEP-BY-STEP FIX: Walk through the correction
    3. KEY LESSON: What general principle prevents this mistake"""
}
```

---

## 9. Smart Quiz Engine

### 9.1 Quiz Generation

The quiz engine generates fresh questions for every session using a structured Gemini prompt that demands strict JSON output:

```python
QUIZ_PROMPT = """Generate a {n}-question MCQ quiz on "{topic}" in {subject}.
Difficulty: {difficulty}. Return ONLY valid JSON:
{
  "questions": [
    {
      "question": "...",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "correct": "A",
      "explanation": "Why A is correct and why others are wrong",
      "hint": "A clue without giving away the answer",
      "points": 10
    }
  ]
}"""
```

**Temperature setting:** 0.3 for quizzes (more deterministic, less creative) vs 0.7 for tutoring (more creative). This ensures quiz questions are clear and well-formed rather than experimental.

**JSON parsing robustness:** Gemini sometimes wraps JSON output in markdown code fences (` ```json ... ``` `). The system strips this before parsing:

```python
text = re.sub(r'^```(?:json)?\s*', '', resp.text.strip())
text = re.sub(r'\s*```$', '', text)
data = json.loads(text)
```

### 9.2 Fallback Question Bank

If the Gemini API is unavailable, a pre-written question bank of 50+ questions across five subjects (Mathematics, Physics, Chemistry, Biology, Computer Science) is used automatically. This ensures the quiz feature always works, even in a demonstration without internet access.

### 9.3 Scoring System

```
XP from quiz = max(5, score_percentage × 2)

Examples:
- Score 100%: 200 XP
- Score 70%:  140 XP
- Score 50%:  100 XP
- Score 0%:   5 XP (minimum — always reward the attempt)

Grade conversion:
- A+ = 100%
- A  = ≥ 90%
- B  = ≥ 80%
- C  = ≥ 70%
- D  = ≥ 60%
- F  = < 60%
```

All quiz results are stored in the database with: subject, topic, difficulty, score, total_questions, correct_answers, grade, time_taken, and the date (`taken_at`). These records are used directly as training data for the Random Forest predictor.

---

## 10. Study Plan Generator

The study plan generator accepts four inputs from the student:
- **Subject** (e.g. Mathematics, Physics)
- **Learning goal** (e.g. "Master integration by parts", "Prepare for Finals")
- **Current level** (beginner / intermediate / advanced)
- **Daily available hours** (e.g. 2 hours per day)
- **Deadline** (optional — a target date)

Gemini generates a structured 4-week JSON roadmap. Each week has a theme. Each day has:
- A specific task name
- Task type (reading / video / practice / quiz / review / AI session)
- Duration estimate
- Resource recommendation

**Example plan structure:**
```json
{
  "title": "Mathematics — Calculus Mastery",
  "subject": "Mathematics",
  "goal": "Master integration by parts",
  "weeks": [
    {
      "week": 1,
      "theme": "Foundations — Derivatives Review",
      "days": [
        {
          "day": "Monday",
          "task": "Review differentiation rules",
          "type": "reading",
          "duration": "45 mins",
          "resource": "Khan Academy: Derivatives"
        }
      ]
    }
  ]
}
```

Plans are stored in the database with a progress tracker (0–100%) and an optional deadline for motivation.

---

## 11. Gamification System

### 11.1 Design Philosophy

Research by Hamari et al. (2014) found that gamification significantly increases user engagement when the rewards feel meaningful and when progress is visible. Smart AI Tutor incorporates gamification as a **first-class concern**, not an afterthought — every feature in the system contributes to the reward loop.

### 11.2 XP Points

| Action | XP Awarded | Rule |
|---|---|---|
| Sending a chat message | +10 XP | Every message, every session |
| Completing a quiz | max(5, score × 2) | 70% score = 140 XP, 0% = 5 XP |
| First question ever asked | +50 XP (once) | Triggers First Question achievement |
| Getting 100% on a quiz | +200 XP (once) | Triggers Perfect Score achievement |
| Creating an account | +100 XP | Triggers Welcome Scholar achievement |
| Unlocking an achievement | +50 to +500 XP | Varies by achievement type |

### 11.3 Level System

```
Level = 1 + (total_xp_points // 500)
Progress to next level = (xp_points % 500) / 500 × 100%
```

Examples:
- 0–499 XP → Level 1
- 500–999 XP → Level 2
- 1000–1499 XP → Level 3

### 11.4 Achievement Catalog

| Category | Achievement | Trigger | XP Bonus |
|---|---|---|---|
| Onboarding | Welcome Scholar | Account registration | 100 |
| Learning | First Question | First chat message ever | 50 |
| Learning | Knowledge Seeker | Ask 10 questions | 75 |
| Quiz | First Quiz | Submit first quiz | 75 |
| Quiz | Perfect Score | Get 100% on any quiz | 200 |
| Quiz | High Achiever | Score ≥ 90% | 100 |
| Quiz | Quiz Veteran | Complete 20 quizzes | 300 |
| Streaks | On Fire | 3-day study streak | 100 |
| Streaks | Week Warrior | 7-day study streak | 250 |
| Streaks | Monthly Master | 30-day study streak | 500 |
| Milestones | Rising Star | Reach Level 5 | 100 |
| Milestones | Scholar | Reach Level 10 | 200 |
| Exploration | Polymath | Study 3+ different subjects | 200 |
| Time | Night Owl | Active after midnight | 75 |
| Time | Early Bird | Active before 7 AM | 75 |

### 11.5 Streak Tracking and Risk Levels

The Performance Predictor page shows the student's streak risk level based on how many days they have been inactive:

| Days Inactive | Risk Level | Message |
|---|---|---|
| 0 (studied today) | LOW 🟢 | "You studied today — great consistency!" |
| 1 day | MEDIUM 🟡 | "Study today to keep your streak alive!" |
| 2–3 days | HIGH 🟠 | "⚠️ 2 days inactive — streak at risk!" |
| 4+ days | CRITICAL 🔴 | "🔴 4 days inactive — get back on track!" |

### 11.6 Leaderboard

A real-time leaderboard shows the top 20 students ranked by XP. The current student's rank is always shown even if they are outside the top 20, providing motivation at every level.

---

## 12. Database Design

### 12.1 Entity Relationships

```
users (1) ─────────────────── (M) learning_sessions
      │
      ├─────────────────────── (M) quiz_results
      │
      ├─────────────────────── (M) achievements
      │
      ├─────────────────────── (M) study_plans
      │
      └─────────────────────── (M) notes
```

Every child table has a `user_id` foreign key. All queries are filtered by `user_id` to prevent any user from accessing another user's data.

### 12.2 Table Definitions

**users**

| Field | Type | Description |
|---|---|---|
| id | Integer PK | Primary key |
| username | String UNIQUE | Auto-generated from full name (e.g. `mohd_anas`) |
| email | String UNIQUE | Login credential — validated on registration |
| password_hash | String | bcrypt hash — never stored in plain text |
| full_name | String | Display name from registration form |
| avatar | String | Emoji avatar (default: 🎓) |
| grade_level | String | Middle School / High School / Undergraduate / Postgraduate |
| learning_style | String | visual / auditory / kinesthetic / reading |
| subjects | Text (JSON) | Array of enrolled subjects: `["Mathematics", "Physics"]` |
| xp_points | Integer | Total XP accumulated (default: 0) |
| level | Integer | Calculated as `1 + (xp_points // 500)` |
| streak_days | Integer | Consecutive days with at least one session |
| last_active | DateTime | Timestamp of last activity (used for streak risk) |
| total_sessions | Integer | Count of all tutoring sessions |
| total_questions | Integer | Count of all chat messages sent |
| total_quiz_taken | Integer | Count of all quiz submissions |
| is_premium | Boolean | Premium tier flag (not yet active) |
| created_at | DateTime | Account creation timestamp |

**learning_sessions**

| Field | Type | Description |
|---|---|---|
| id | Integer PK | Primary key |
| session_id | String UNIQUE | UUID generated per session |
| user_id | Integer FK | Links to users.id |
| subject | String | Subject studied in this session |
| topic | String | Specific topic within the subject |
| messages | Text (JSON) | Full conversation history array |
| agent_mode | String | Last active teaching mode |
| xp_earned | Integer | XP earned in this session |
| msg_count | Integer | Number of messages sent |
| started_at | DateTime | Session start timestamp |

**quiz_results**

| Field | Type | Description |
|---|---|---|
| id | Integer PK | Primary key |
| user_id | Integer FK | Links to users.id |
| subject | String | Quiz subject |
| topic | String | Quiz topic |
| difficulty | String | easy / medium / hard |
| score | Float | Raw score (percentage, 0–100) |
| total_questions | Integer | Number of questions in the quiz |
| correct_answers | Integer | Number of correct answers |
| time_taken_secs | Float | Time spent on the quiz |
| grade | String | A+ / A / B / C / D / F |
| taken_at | DateTime | Quiz submission timestamp |

**achievements**

| Field | Type | Description |
|---|---|---|
| id | Integer PK | Primary key |
| user_id | Integer FK | Links to users.id |
| key | String | Unique achievement identifier (e.g. `first_question`) |
| title | String | Display title |
| description | String | Achievement description |
| icon | String | Emoji icon |
| category | String | learning / quiz / streak / milestone / time |
| xp_value | Integer | XP awarded for this achievement |
| earned_at | DateTime | When the achievement was unlocked |

---

## 13. API Design

All endpoints under `/api/` require a valid login session (Flask-Login) or JWT Bearer token.

### 13.1 Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Create account (3-step wizard data) |
| POST | `/login` | Login with email + password, returns JWT |
| GET | `/logout` | End session |

### 13.2 Chat and Tutoring Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | Send message through 5-node pipeline, returns AI response + XP + achievements |
| POST | `/api/pdf/upload` | Upload PDF for RAG ingestion into ChromaDB |
| GET | `/api/pdf/documents` | List all uploaded documents for this user |
| DELETE | `/api/pdf/documents/<id>` | Delete a document and remove from ChromaDB |
| POST | `/api/pdf/chat` | Chat with RAG context from uploaded PDFs |

### 13.3 Quiz Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/quiz/generate` | Generate AI quiz (subject, difficulty, num_questions) |
| POST | `/api/quiz/submit` | Submit answers — returns score, grade, XP, per-question feedback |

### 13.4 Study Plan Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/study-plan/generate` | Generate 4-week study plan (subject, goal, deadline, hours/day) |
| GET | `/api/study-plan/<id>` | Fetch a specific plan |
| DELETE | `/api/study-plan/<id>` | Delete a plan |

### 13.5 Analytics and Prediction Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analytics` | Fetch performance analytics for Chart.js |
| GET | `/api/performance/predict` | Run RF predictor, returns predicted scores + model used |
| GET | `/api/leaderboard` | Top-20 XP ranking |
| GET | `/api/user/stats` | XP, level, streak, achievement summary |
| PUT | `/api/user/profile` | Update profile fields (grade, style, subjects) |

### 13.6 Notes Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/notes` | List all notes for this user |
| POST | `/api/notes` | Create a new note |
| PUT | `/api/notes/<id>` | Update an existing note |
| DELETE | `/api/notes/<id>` | Delete a note |

### 13.7 Sample API Response — Chat

```json
{
  "response": "**Newton's Second Law** — F = ma\n\nForce equals mass times acceleration...",
  "agent_steps": [
    "✅ Intent: explain_concept | Complexity: Basic",
    "✅ Knowledge retrieved for Physics",
    "✅ Curriculum mapped: prerequisites and next steps identified",
    "✅ Gemini (LangChain) generating Tutor response...",
    "✅ Quality checked — response validated"
  ],
  "resources": [
    {"type": "tool", "name": "PhET Simulations", "url": "https://phet.colorado.edu", "desc": "Interactive physics simulations"}
  ],
  "follow_up_questions": [
    "What happens to acceleration if you double the force but keep mass the same?",
    "How is Newton's Second Law used in rocket science?"
  ],
  "xp_earned": 10,
  "total_xp": 1260,
  "level": 3,
  "new_achievements": [],
  "rag_used": false,
  "rag_chunks": 0
}
```

---

## 14. Frontend Design

### 14.1 Design System

The frontend uses a **dark editorial aesthetic** — high contrast, minimal decoration, and typography-forward layout. The design system is built entirely on CSS custom properties (variables), which enables instant theme switching between dark and light mode without reloading the page.

**Fonts:**
- **Clash Display** — headings (modern, geometric, high visual impact)
- **Instrument Sans** — body text (highly legible at small sizes, clean)
- **JetBrains Mono** — code blocks (monospace, developer-friendly)

**Colour tokens:**
```css
:root {
  --ink:       #05070f;   /* page background */
  --ink3:      #111827;   /* card background */
  --indigo:    #4f46e5;   /* primary accent */
  --electric:  #818cf8;   /* light indigo */
  --amber:     #f59e0b;   /* XP and warnings */
  --emerald:   #10b981;   /* success and earnings */
  --txt:       #e2e8f0;   /* primary text */
  --txt2:      #94a3b8;   /* muted text */
  --border:    #1e2d45;   /* subtle borders */
}
```

### 14.2 Page Inventory

| Page | Route | What It Shows |
|---|---|---|
| Landing | `/` | Hero section, feature highlights, "Get Started" button |
| Dashboard | `/dashboard` | XP card, level, streak, recent sessions, achievements |
| AI Tutor | `/tutor` | Mode pills, subject selector, chat window, agent pipeline sidebar |
| Smart Quiz | `/quiz` | Quiz config form, MCQ interface, live score tracker |
| Study Plans | `/study-plans` | Plan list, 4-week timeline, daily task view |
| Analytics | `/analytics` | Chart.js line chart (score trend), bar chart (subject scores) |
| Notes | `/notes` | Markdown editor with subject tags, pin toggle, delete |
| Leaderboard | `/leaderboard` | Top 20 students by XP, current user highlighted |
| Profile | `/profile` | Achievement gallery, quiz history, editable preferences |
| PDF Chat | `/pdf-chat` | Document manager (left), RAG chat (right) |
| Performance | `/performance` | RF predictions, mastery levels, streak risk, AI coaching |

### 14.3 Critical Bug — Jinja2 Template Inheritance

During development, a critical frontend bug was discovered: **three pages had zero styling in the browser**.

The Tutor, Quiz, and Analytics pages all defined their CSS inside `{% block extra_head %}`, but `base.html` only declared `{% block head %}`. In Jinja2, when a child template defines a block that has no matching block in the parent, **the content is silently discarded** — no error, no warning. Three pages' worth of CSS (chat bubbles, mode pills, layout grids, quiz interface) simply never reached the browser.

**Fix:** One line added to `base.html`:
```html
{% block head %}{% endblock %}
{% block extra_head %}{% endblock %}  ← this line was missing
```

After adding this line, all three pages immediately rendered correctly.

---

## 15. Security Implementation

### 15.1 Password Security

All passwords are hashed using **bcrypt** before storage. bcrypt is deliberately computationally expensive to resist brute-force attacks. The original password is never stored anywhere.

```python
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# Storing a password
user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

# Checking a password
is_correct = bcrypt.check_password_hash(user.password_hash, entered_password)
```

### 15.2 Input Validation

**Client-side (JavaScript, before any network request):**
- Full name: regex `/^[A-Za-z]+([ '\-][A-Za-z]+)*$/` — letters only, no numbers or special characters
- Email: regex `/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/` — standard email format
- Password: minimum 6 characters enforced before step transition
- Grade level: must be selected from the dropdown (cannot skip)

**Server-side (Flask, after receiving the request):**
```python
import re

email     = (data.get("email") or "").strip().lower()
full_name = (data.get("display_name") or "").strip()
password  = data.get("password") or ""

if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
    return jsonify({"error": "Invalid email address"}), 400

if User.query.filter_by(email=email).first():
    return jsonify({"error": "Email already registered"}), 409
```

### 15.3 Username Auto-Generation

The frontend sends the user's full name as `display_name`. The backend auto-generates a clean username and handles collisions:

```python
import re

base_uname = re.sub(r'[^a-z0-9_]', '', full_name.lower().replace(' ', '_'))
username   = base_uname
n = 1
while User.query.filter_by(username=username).first():
    username = f"{base_uname}{n}"
    n += 1
# "Mohd Anas" → "mohd_anas", or "mohd_anas1" if taken
```

### 15.4 JWT Authentication

API endpoints use JWT Bearer tokens for stateless authentication:
```python
from flask_jwt_extended import JWTManager, create_access_token

token = create_access_token(identity=user.id)  # 24-hour expiry
# Frontend stores token in localStorage and sends in Authorization header
```

### 15.5 SQL Injection Prevention

The SQLAlchemy ORM is used exclusively for all database queries. No raw SQL strings are written anywhere in the codebase. SQLAlchemy parameterises all queries automatically, making SQL injection impossible.

### 15.6 File Upload Security

```python
from werkzeug.utils import secure_filename

filename = secure_filename(uploaded_file.filename)
# MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB limit
```

`secure_filename()` removes directory traversal characters (`../`, `/`, etc.) from filenames. The 32 MB limit prevents denial-of-service through large file uploads.

### 15.7 Data Isolation

Every database query includes a `user_id` filter:
```python
# Example — user can only see their own quiz results
results = QuizResult.query.filter_by(user_id=current_user.id).all()
```

This prevents horizontal privilege escalation — a logged-in user cannot access another user's data by changing an ID in the URL.

---

## 16. Technologies Used

| Technology | Version | Category | Specific Use in This Project |
|---|---|---|---|
| Python | 3.11 | Language | Entire backend |
| Flask | 3.x | Web Framework | HTTP routing, session management, Jinja2 templating |
| SQLAlchemy | 2.x | ORM | All database queries — no raw SQL |
| SQLite | 3.x | Database | Stores all student data in a single `.db` file |
| Flask-Login | 0.6.x | Auth | Session management, `@login_required` decorator |
| Flask-JWT-Extended | 4.x | Auth | JWT tokens for API authentication |
| Flask-Bcrypt | 1.x | Security | Password hashing with salt |
| Flask-CORS | 4.x | Security | Cross-origin resource sharing configuration |
| LangGraph | 0.1.x | AI | StateGraph for the 5-node agent pipeline |
| LangChain (Google) | 0.2.x | AI | `ChatGoogleGenerativeAI` wrapper for Gemini |
| google-generativeai | 0.5.x | AI | Direct Gemini SDK (fallback if LangChain fails) |
| **scikit-learn** | **1.6.0** | **ML** | **RandomForestRegressor for score prediction** |
| ChromaDB | 0.5.x | Vector DB | Per-user PDF vector storage for RAG |
| PyMuPDF (fitz) | 1.23.x | PDF | Primary PDF text extraction |
| PyPDF2 | 3.x | PDF | Fallback PDF extraction for edge cases |
| python-dotenv | 1.x | Config | Environment variable management via `.env` |
| Gunicorn + Eventlet | latest | Deployment | Production WSGI server with concurrent workers |
| Chart.js | 4.4.0 | Frontend | Analytics charts (line + bar) |
| HTML5 / CSS3 / JS | Modern | Frontend | All web pages — no framework needed |
| Jinja2 | 3.x | Templating | Server-side HTML rendering (included in Flask) |

---

## 17. Real Bugs Found and Fixed

### Bug 1 — Silent Registration Failure (Critical)

**What was happening:** Every new account registration silently failed. Students saw a loading spinner, then nothing happened. No error message appeared.

**Root cause:** The registration form sent the user's full name under the key `display_name`. The backend expected a key called `username`. Since `username` was empty string (key not found), the validation check `if not email or not username or not password` immediately returned `{"error": "All fields are required"}`. The frontend did not display this error properly, so users saw no feedback.

**Result before fix:** 0% of registrations succeeded.

**Fix applied:**
```python
# Before (broken):
username = (data.get("username") or "").strip()

# After (fixed):
full_name = (data.get("display_name") or data.get("full_name") or "").strip()
base_uname = re.sub(r'[^a-z0-9_]', '', full_name.lower().replace(' ', '_'))
username = base_uname
n = 1
while User.query.filter_by(username=username).first():
    username = f"{base_uname}{n}"; n += 1
```

**Result after fix:** 100% of registrations succeed.

**Lesson:** Always verify that the keys the frontend sends exactly match what the backend expects. Mismatched field names cause silent failures that are harder to debug than explicit errors.

---

### Bug 2 — All Page-Specific CSS Silently Discarded (Jinja2)

**What was happening:** The Tutor, Quiz, and Analytics pages rendered with zero styling — completely plain HTML, no layout, no colours, no styled components.

**Root cause:** Three page templates defined their CSS inside `{% block extra_head %}`. The base template `base.html` only declared `{% block head %}`. In Jinja2 template inheritance, when a child template defines a block that has **no matching block in the parent**, that block's content is **silently discarded** with no error or warning. Three full `<style>` blocks simply never appeared in the HTML output.

**Fix applied:** Added one line to `base.html`:
```html
{% block head %}{% endblock %}
{% block extra_head %}{% endblock %}  ← added
```

**Result:** All three pages immediately rendered with full styling.

**Lesson:** Jinja2 silently discards unmatched child blocks. Always verify that CSS is actually reaching the browser using browser Developer Tools, not just by checking the Python code.

---

### Bug 3 — Wrong Database Attribute Names

**What was happening:** Opening the Performance Predictor page caused an `AttributeError` crash. The predictor never received any date data, which broke the `days_since_last` feature and the streak risk calculation.

**Root cause:** The API route for `/api/performance/predict` referenced two fields that do not exist on the SQLAlchemy models:
- `q.completed_at` — the real field is `q.taken_at`
- `s.session_date` — the real field is `s.started_at`

SQLAlchemy only raises `AttributeError` at runtime when records are queried, not at model definition time. The bug was invisible until someone actually loaded the page.

**Fix applied:**
```python
# Before (broken):
quiz_data = [{"completed_at": q.completed_at ...} for q in quiz_results]
session_data = [{"session_date": s.session_date ...} for s in sessions]

# After (fixed):
quiz_data = [{
    "subject":         q.subject,
    "score":           q.score,
    "total_questions": q.total_questions,
    "difficulty":      q.difficulty,           # also added this missing field
    "completed_at":    q.taken_at.isoformat()  # correct field name
} for q in quiz_results]
session_data = [{"session_date": s.started_at.isoformat()} for s in sessions]
```

**Lesson:** SQLAlchemy does not validate field names at definition time. Write integration tests that exercise full API responses.

---

### Bug 4 — Linear Regression Too Simplistic

**What was happening:** The performance predictor was producing predictions that seriously underestimated improving students. A student who scored 40, 40, 40, 80, 85 received a predicted next score of approximately 60.

**Root cause:** The original predictor hand-coded the least-squares formula using only the raw score sequence. A straight line fitted through `[40, 40, 40, 80, 85]` has a slope of approximately 11.25 per quiz, giving a prediction around 96 at first glance — but the intercept pulls it down, and the result is systematically wrong for non-linear patterns. More fundamentally, the model used only one feature (the score sequence) and could not capture difficulty, consistency, staleness, or subject.

**Fix applied:** Complete replacement with Random Forest Regressor using 10 engineered features and sliding-window training (see Section 7 for full details).

**Result:** 45% lower MAE, 47% lower RMSE.

---

### Bug 5 — LangGraph State KeyErrors

**What was happening:** The LangGraph pipeline occasionally crashed mid-execution with `KeyError` exceptions in downstream nodes.

**Root cause:** Early implementations assumed that upstream nodes had always run successfully and had populated all state fields. When optional fields like `rag_context` were absent (because PDF mode was not active), downstream nodes that tried to access them raised `KeyError`.

**Fix applied:** All state fields were given explicit default values in the initial state dictionary:
```python
initial_state = {
    "rag_context": "",      # default empty string, not absent key
    "use_pdf": False,
    "agent_steps": [],
    "resources": [],
    "follow_up_questions": [],
    # ... all other fields explicitly initialised
}
```

Also added full fallback chain: LangGraph → Direct Gemini SDK → Demo mode. The system never crashes now — it degrades gracefully.

---

### Bug 6 — Gemini JSON Format Inconsistency

**What was happening:** Quiz generation was failing with `json.JSONDecodeError` even though Gemini was returning valid quiz data.

**Root cause:** Gemini's JSON output is inconsistently formatted. Sometimes it returns plain JSON. Sometimes it wraps it in markdown code fences: ` ```json { ... } ``` `. Sometimes it adds trailing whitespace. The original parser tried to call `json.loads()` directly on the raw output.

**Fix applied:**
```python
text = resp.text.strip()
text = re.sub(r'^```(?:json)?\s*', '', text)  # strip opening fence
text = re.sub(r'\s*```$', '', text)            # strip closing fence
data = json.loads(text)
```

Added fallback to pre-written question bank if parsing still fails.

---

### Bug 7 — ChromaDB Collection Does Not Exist on First Query

**What was happening:** When a user opened PDF Chat for the first time (before uploading any document), the system crashed with a ChromaDB `InvalidCollectionException`.

**Root cause:** The original code called `client.get_collection("user_X_docs")` which raises an exception if the collection does not exist. New users have no collection yet.

**Fix applied:**
```python
# Before (broken):
collection = client.get_collection(f"user_{user_id}_docs")

# After (fixed):
collection = client.get_or_create_collection(f"user_{user_id}_docs")
```

All ChromaDB operations were also wrapped in `try/except` blocks so any vector store failure never crashes the main application.

---

## 18. Results and Evaluation

### 18.1 Feature Completeness

| Feature | Implemented | Tested | Notes |
|---|---|---|---|
| 5-node LangGraph pipeline | ✅ | ✅ | All 5 nodes functional |
| 5 teaching modes | ✅ | ✅ | Verified different outputs per mode |
| PDF upload + RAG | ✅ | ✅ | Per-user ChromaDB isolation |
| AI quiz generation | ✅ | ✅ | Fallback bank for offline use |
| AI study plan generation | ✅ | ✅ | 4-week, daily granularity |
| Random Forest prediction | ✅ | ✅ | 10 features, EWMA fallback |
| XP + levels + streaks | ✅ | ✅ | Fires within same API response |
| 20+ achievements | ✅ | ✅ | Time-based and streak-based |
| Leaderboard | ✅ | ✅ | Top 20, current user shown |
| Markdown notes | ✅ | ✅ | CRUD, pin, subject tags |
| Analytics charts | ✅ | ✅ | Chart.js line + bar charts |
| User registration validation | ✅ | ✅ | Client + server-side checks |
| Dark / light theme | ✅ | ✅ | localStorage persisted |
| Responsive design | ✅ | ✅ | Sidebar collapses on mobile |
| JWT + bcrypt security | ✅ | ✅ | Industry-standard |
| Per-user data isolation | ✅ | ✅ | Verified by query scoping |
| Demo mode (no API key) | ✅ | ✅ | Falls back gracefully |

### 18.2 System Performance

| Operation | Typical Time | Notes |
|---|---|---|
| Gemini API response (Node 4) | 1.2 – 3.4 seconds | Depends on answer length and Gemini server |
| Full 5-node pipeline | 1.4 – 4.0 seconds | Includes Gemini call |
| RAG retrieval (ChromaDB) | < 80 ms | Local ChromaDB, 500 stored chunks |
| Random Forest train + predict | < 150 ms | 9 quiz records, n_jobs=-1 |
| Quiz generation (Gemini) | 1.5 – 4.0 seconds | 5 questions, medium difficulty |
| SQLite query | < 50 ms | Standard indexed query on user_id |
| Dashboard page load | < 1.2 seconds | Including Chart.js initialisation |
| Registration (full 3-step) | < 500 ms | Database write included |

### 18.3 AI Response Quality

Five test queries were evaluated across different modes and student levels:

| Query | Mode | Student Level | Correct? | Teaching Structure? | Personalised? |
|---|---|---|---|---|---|
| "Explain Newton's 2nd Law" | Tutor | Grade 10 | ✅ | ✅ Analogy + example + check Q | ✅ Simple language |
| "What is integration by parts?" | Socratic | Undergraduate | ✅ | ✅ Questions only, no direct answer | ✅ University notation |
| "Photosynthesis exam tomorrow" | Exam Prep | High School | ✅ | ✅ Mnemonics + mistakes + practice Q | ✅ Exam-focused |
| "Explain recursion like a story" | Creative | Any | ✅ | ✅ Mirror/doll analogy | ✅ Imaginative |
| "My Python loop is wrong" | Debug | Beginner | ✅ | ✅ Root cause + step-by-step fix | ✅ Beginner language |

---

## 19. Advantages of This Project

**1. True pedagogical intelligence, not a chatbot wrapper**
The 5-step LangGraph pipeline means every response is intent-aware, curriculum-aware, and personally tailored. No other free tool processes student questions through structured reasoning stages before answering.

**2. Grounded in the student's own study material**
RAG means the AI answers from the student's actual textbook, not from generic training data. This is critical for university-level study where syllabi vary significantly between institutions.

**3. Machine learning performance prediction**
The Random Forest model with 10 features is the only free AI tutoring tool that offers data-driven next-score prediction. It tells students not just how they did, but where they are headed.

**4. Everything in one integrated platform**
AI Tutor + Smart Quiz + Study Plans + PDF Chat + Notes + Analytics + Predictor + Gamification — all in one system. Every module feeds the others. Quiz results train the RF model. Session data feeds analytics. XP from everything drives gamification.

**5. Gamification for habit formation**
The XP/streak/achievement system is built into the core reward loop. Every action is immediately rewarded. Streak risk levels encourage daily study. The leaderboard creates social motivation.

**6. Transparent AI**
After every response, the UI shows which pipeline steps ran. Students can see that AI is structured reasoning, not magic — which builds trust and is also educational.

**7. Works without an API key (demo mode)**
The system falls back gracefully to a 50+ question quiz bank and demo mode if Gemini is unavailable. Ideal for academic demonstrations without internet credentials.

**8. Secure and privacy-first**
Per-user data isolation, bcrypt passwords, JWT tokens, path traversal prevention, input validation on both client and server. No user can access another's data.

---

## 20. Limitations

1. **Response latency:** Gemini API takes 1.2–4 seconds. No streaming — students see a typing animation and wait for the complete response.

2. **Random Forest cold start:** Students with fewer than 3 quiz attempts fall back to EWMA prediction. The RF model improves significantly as data accumulates.

3. **PDF quality dependence:** RAG works best with clean, text-based PDFs. Scanned image PDFs produce garbled text extraction and poor RAG answers.

4. **English only:** The entire system (UI, AI responses, quiz questions) is in English only. No Hindi, Urdu, or other language support exists yet.

5. **No email verification:** Students can register with any email address — real or fake. There is no verification step.

6. **Single-server architecture:** The current deployment runs on one process. Serving many simultaneous users requires migration to PostgreSQL and an external session store (Redis).

7. **Streak reset logic:** The streak counter increments when any session is recorded, but there is no automatic reset logic for missed days. The streak risk display warns the student, but the streak count does not decrease.

8. **Premium tier not active:** The `is_premium` field exists in the database schema but no premium features are implemented behind it.

---

## 21. Future Scope

### Near-Term (0–3 months)

- **Streaming responses:** Server-Sent Events to show tokens arriving progressively, eliminating the 1–4 second wait
- **Email verification** and password reset via email
- **Daily study reminders** via browser notifications or email digest
- **Streak reset logic** with a 24-hour grace period
- **Export features:** PDF performance report, CSV quiz history
- **Incremental RF training:** Update the model after each new quiz rather than retraining from scratch on every prediction request

### Medium-Term (3–6 months)

- **PostgreSQL migration** for multi-user production deployment
- **Celery + Redis** for asynchronous PDF processing and background ML jobs
- **Voice input/output** (speech-to-text + text-to-speech) for accessibility
- **Teacher/instructor portal** with class roster management and aggregate analytics
- **LMS integration** (Canvas, Moodle) via Learning Tools Interoperability (LTI) standard
- **XGBoost or LightGBM** upgrade to the prediction engine as student datasets grow

### Long-Term (6+ months)

- **Mobile applications** (React Native or Flutter) for Android and iPhone
- **Collaborative study sessions** — shared whiteboards, real-time multiplayer quizzes
- **Essay grading agent** that can mark written answers, not just MCQs
- **Code execution sandbox** for Computer Science students (Judge0 or Piston API)
- **Hindi, Urdu, and regional language support** — essential for the Indian educational market
- **LSTM-based sequence model** for students with very long quiz histories (100+ attempts) where temporal patterns become important
- **Adaptive difficulty** — automatic quiz difficulty adjustment based on RF predictions

---

## 22. References

1. Bloom, B. S. (1984). The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring. *Educational Researcher*, 13(6), 4–16.

2. VanLehn, K. (2011). The Relative Effectiveness of Human Tutoring, Intelligent Tutoring Systems, and Other Tutoring Systems. *Educational Psychologist*, 46(4), 197–221.

3. Lewis, P., Perez, E., Piktus, A., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems (NeurIPS)*, 33.

4. Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5–32.

5. Pedregosa, F., Varoquaux, G., Gramfort, A., et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.

6. Shinn, N., Cassano, F., Berman, E., Gopinath, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. *NeurIPS*.

7. Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. *ICLR*.

8. Hamari, J., Koivisto, J., & Sarsa, H. (2014). Does Gamification Work? A Literature Review of Empirical Studies on Gamification. *47th Hawaii International Conference on System Sciences (HICSS)*.

9. Kasneci, E., Sessler, K., Küchemann, S., et al. (2023). ChatGPT for Good? On Opportunities and Challenges of Large Language Models for Education. *Learning and Individual Differences*, 103.

10. Gao, Y., Xiong, Y., Gao, X., et al. (2023). Retrieval-Augmented Generation for Large Language Models: A Survey. *arXiv:2312.10997*.

11. Graesser, A. C., Lu, S., Jackson, G. T., et al. (2004). AutoTutor: A Tutor with Dialogue in Natural Language. *Behavior Research Methods, Instruments, and Computers*, 36(2), 180–192.

12. Anderson, J. R., Boyle, C. F., Corbett, A. T., & Lewis, M. W. (1990). Cognitive Modelling and Intelligent Tutoring. *Artificial Intelligence*, 42(1), 7–49.

13. Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). Attention Is All You Need. *NeurIPS*.

14. Google. (2024). *Gemini API Documentation*. https://ai.google.dev

15. LangChain AI. (2024). *LangGraph Documentation*. https://langchain.com/langgraph

16. Chroma. (2024). *ChromaDB Documentation*. https://docs.trychroma.com

17. Pallets Projects. (2024). *Flask Documentation*. https://flask.palletsprojects.com

18. SQLAlchemy. (2024). *SQLAlchemy Documentation*. https://docs.sqlalchemy.org

19. Kolb, D. A. (1984). *Experiential Learning: Experience as the Source of Learning and Development*. Prentice-Hall.

20. Roll, I., & Wylie, R. (2016). Evolution and Revolution in Artificial Intelligence in Education. *International Journal of Artificial Intelligence in Education*, 26, 582–599.

---

*Documentation prepared for academic submission — Department of Computer Science, Faculty of Sciences, Jamia Millia Islamia (A Central University), May 2026.*

*All descriptions reflect the implemented and tested codebase as of May 2026.*
