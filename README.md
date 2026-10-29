# Python Quiz Application - Smart Learning Engine
**DIGIT Innovations Internship Assignment Submission**  
**Candidate Name:** Akshaya  
**Track:** Level 1 Mandatory Implementation (Complete & Verified)  
**Submission Date:** October 29, 2026  
**Public Live URL:** [https://ais-pre-p67ax6eq33qolvrmngkczb-989727123617.asia-east1.run.app](https://ais-pre-p67ax6eq33qolvrmngkczb-989727123617.asia-east1.run.app)

---

## 📖 Project Overview
The **Python Quiz Application** is a full-stack assessment web application designed to evaluate learner proficiency across core Python computer science concepts. It replaces previous disconnected and insecure client-side scoring with an authoritative, database-driven architecture. 

All question data, answer evaluations, attempt scoring, and audit histories are managed securely through a centralized SQLite database and Python Flask backend.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.10+ / 3.11+, Flask 3.0.0, Gunicorn 21.2.0, Flask-CORS 4.0.0
- **Database:** SQLite 3 (ACID-compliant relational database with foreign keys and indexes)
- **Frontend:** Responsive Mobile-First HTML5, Touch-Optimized CSS, Modern JavaScript (No-freeze custom modals, touch targets >= 48px, offline resilience)
- **Mobile Compatibility:** iPhone (Safari/Chrome), Android (Chrome/Firefox/Samsung Internet), iPad/Tablets, and Desktop PC/Mac
- **Automated Testing:** Pytest 8.0.0 (13 isolated automated tests)
- **Deployment:** Render / Cloud Run / Linux Procfile (`gunicorn app:app`)

---

## 📱 Mobile & Desktop Execution Guide

### Why was it not working on phone originally?
1. **Desktop-only Layout:** Original font sizes and 7-column attempts table caused horizontal screen breaking on phones.
2. **Blocking Native Popups:** Browser native `window.alert()` and `window.confirm()` frequently freeze, get silenced, or fail inside mobile WebViews or mobile Safari.
3. **Double-Click File Opening on Phone:** If the ZIP was opened directly on a smartphone (e.g. via iPhone Files or Android Downloads) without running the Flask server, `fetch('/api/questions')` would fail with a network error.

### How it is now Fixed for Phones:
1. **Touch Targets & Fluid Layout:** All option buttons are at least 52px tall with comfortable tap padding, clear letter badges, and haptic feedback.
2. **Custom Non-blocking Modals:** Replaced native `alert()` and `confirm()` with custom animated glassmorphism modals that never freeze mobile browsers.
3. **Dual Operation (Server + Standalone Mobile Fallback):**
   - **With Flask Server:** Connects to authoritative SQLite database.
   - **Direct Mobile File Opening:** If opened directly in any mobile browser without Python, it automatically activates the standalone mobile engine with offline persistence in LocalStorage!
4. **Running Python Backend on Mobile:**
   - **Android:** Install **Pydroid 3** or **Termux** from Play Store / F-Droid, navigate to the folder, run `pip install -r requirements.txt` and `python app.py`. Open `http://localhost:5000` in Chrome.
   - **iOS:** Open in Safari directly, or run with **Pythonista 3** or **a-Shell**.
   - **Hosted Web App:** Simply navigate to the live URL on your phone's browser!

---

## ✨ Features Implemented (Level 1 Requirements)

1. **Single Authoritative Source of Truth:**
   - All questions, answer options, correct answer keys, difficulty tiers, hints, and explanations are stored in SQLite (`quiz.db`).
   - Duplicate hardcoded question arrays have been completely removed from both `app.py` and the client JavaScript.

2. **Security & Anti-Cheating Architecture:**
   - The `/api/questions` endpoint transmits only public quiz information (IDs, topics, questions, code snippets, and 4 choices).
   - Correct answers (`correct_index`) and educational explanations are strictly withheld on the server until the quiz is submitted.

3. **Authoritative Backend Answer Validation:**
   - The backend validates student choices against SQLite records.
   - Computes score, percentage, performance tier (`A+`, `A`, `B`, `C`, `D`), and pass/fail status.
   - Prevents duplicate submissions using unique attempt UUIDs.

4. **Permanent Relational Persistence:**
   - Every completed quiz attempt is saved in the `quiz_attempts` table.
   - Every individual question response (including chosen answer and correctness) is logged in `student_responses`.
   - Results persist across server restarts and reconnections.

5. **Enhanced User Experience & Results Review:**
   - Clean Start Screen with candidate credentials and rules overview.
   - Single-question interactive presentation with live countdown timer (15:00 minutes).
   - Prevents accidental submission without selecting an answer (or allows explicit skipping).
   - Question-by-question review showing student pick, correct pick, and explanations.
   - View past attempt history directly from SQLite.
   - Working Quiz Restart button with clean timer resets.

---

## 📁 Project Folder Structure

```
.
├── app.py                     # Primary Flask backend server & REST API routes
├── database.py                # SQLite connection manager, queries, and transactions
├── schema.sql                 # Relational schema DDL (questions, attempts, responses)
├── seed.py                    # Database initialization and question seed script
├── templates/
│   └── index.html             # Full-stack frontend template (HTML5/CSS3/JavaScript)
├── tests/
│   ├── __init__.py
│   └── test_quiz.py           # 13 automated tests covering all functional requirements
├── requirements.txt           # Python dependencies (Flask, Gunicorn, Flask-CORS, Pytest)
├── Procfile                   # Process file for production deployment
├── render.yaml                # Render platform infrastructure-as-code configuration
├── SUBMISSION_URL.txt         # Live public deployment details
├── INTERNSHIP_REPORT.doc      # Comprehensive internship evaluation and technical report
└── README.md                  # Complete documentation and setup guide
```

---

## 🗄️ Database Schema Explanation

The SQLite database consists of three normalized tables:

### 1. `questions` Table
Stores the authoritative question bank.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `topic` (TEXT NOT NULL): Domain (Variables, Data Types, Operators, Loops, Functions, Lists, OOP)
- `difficulty` (TEXT NOT NULL): Easy, Medium, Hard
- `question` (TEXT NOT NULL): Question stem
- `code_snippet` (TEXT): Associated Python code snippet
- `option_a`, `option_b`, `option_c`, `option_d` (TEXT NOT NULL): Four multiple-choice options
- `correct_index` (INTEGER NOT NULL): 0 (A), 1 (B), 2 (C), or 3 (D)
- `explanation` (TEXT NOT NULL): Detailed pedagogical justification
- `hint` (TEXT): Conceptual hint

### 2. `quiz_attempts` Table
Stores summary records for completed quiz attempts.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `attempt_uuid` (TEXT UNIQUE NOT NULL): Unique session identifier
- `student_name` (TEXT): Name of examinee (default: Akshaya)
- `total_questions` (INTEGER NOT NULL): Total questions in the quiz
- `correct_answers` (INTEGER NOT NULL): Number of correct responses
- `incorrect_answers` (INTEGER NOT NULL): Number of incorrect responses
- `score` (INTEGER NOT NULL): Points earned
- `percentage` (REAL NOT NULL): Accuracy percentage
- `grade` (TEXT NOT NULL): Academic letter grade (e.g., "A+ (Outstanding)")
- `passed` (INTEGER NOT NULL): 1 for pass (>= 60%), 0 for fail
- `time_taken_seconds` (INTEGER): Time spent taking quiz
- `created_at` (TIMESTAMP): UTC attempt timestamp

### 3. `student_responses` Table
Itemized question-level responses for auditing and learning diagnostics.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `attempt_id` (INTEGER NOT NULL, FK -> `quiz_attempts.id` ON DELETE CASCADE)
- `question_id` (INTEGER NOT NULL, FK -> `questions.id`)
- `selected_index` (INTEGER): Student's choice (0-3 or NULL if skipped)
- `is_correct` (INTEGER NOT NULL): 1 if correct, 0 if incorrect
- `created_at` (TIMESTAMP): UTC timestamp

---

## 🔌 API Endpoint Documentation

| Method | Endpoint | Description | Request Body | Response |
|---|---|---|---|---|
| `GET` | `/` | Serves the interactive quiz user interface | None | HTML template |
| `GET` | `/api/health` | Health check & SQLite statistics | None | JSON with question and attempt counts |
| `GET` | `/api/questions` | Returns question bank (omits answers) | None | JSON array of 10 questions |
| `POST` | `/api/submit` | Evaluates answers, saves attempt, returns review | `{ attemptUuid, studentName, timeTakenSeconds, answers: { "1": 0, ... } }` | JSON with score, percentage, grade, review |
| `GET` | `/api/attempts` | Fetches historical quiz attempts from SQLite | Query params: `?limit=20` | JSON array of past attempts |
| `GET` | `/api/attempts/<uuid>` | Fetches itemized responses for a specific attempt | None | JSON object with attempt and responses |

---

## 🚀 Installation & Local Execution

### Prerequisites
- Python 3.8 or higher installed on your system.
- Git (optional, for cloning).

### Step 1: Create and Activate Virtual Environment
```bash
# Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# Windows:
python -m venv venv
venv\Scripts\activate
```

### Step 2: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize and Seed the SQLite Database
```bash
python seed.py
```
*Note: `app.py` also automatically initializes and seeds `quiz.db` on first run if it does not already exist.*

### Step 4: Start the Flask Application
```bash
python app.py
```
The application will start on `http://127.0.0.1:5000`. Open this address in your web browser.

> **Important Note:** Unlike the initial broken draft, this application **cannot** be run by merely double-clicking `templates/index.html` in a file explorer. It is a full-stack application that requires the Flask backend and SQLite database to function correctly.

---

## 🧪 How to Run Automated Tests

The project includes an automated test suite implemented with `pytest` in `tests/test_quiz.py`. Each test uses a temporary, isolated SQLite database to ensure the main `quiz.db` is never affected.

Run the tests with verbose output:
```bash
pytest -v
```

### Test Suite Output Verification:
```
============================= test session starts ==============================
platform linux -- Python 3.11.2, pytest-8.0.0, pluggy-1.7.0
rootdir: /app/applet
collected 13 items

tests/test_quiz.py::test_flask_app_initialization PASSED                 [  7%]
tests/test_quiz.py::test_database_initialization_and_schema PASSED       [ 15%]
tests/test_quiz.py::test_retrieval_of_questions_from_sqlite PASSED       [ 23%]
tests/test_quiz.py::test_availability_of_at_least_10_questions PASSED    [ 30%]
tests/test_quiz.py::test_client_questions_endpoint_does_not_leak_answers PASSED [ 38%]
tests/test_quiz.py::test_correct_answer_evaluation PASSED                [ 46%]
tests/test_quiz.py::test_incorrect_answer_evaluation PASSED              [ 53%]
tests/test_quiz.py::test_mixed_answers_score_and_percentage_calculation PASSED [ 61%]
tests/test_quiz.py::test_invalid_submission_handling PASSED              [ 69%]
tests/test_quiz.py::test_saving_quiz_attempts_and_answers_in_sqlite PASSED [ 76%]
tests/test_quiz.py::test_retrieving_previously_saved_results PASSED      [ 84%]
tests/test_quiz.py::test_restart_persistence_across_connections PASSED   [ 92%]
tests/test_quiz.py::test_duplicate_submission_handling PASSED            [100%]

============================== 13 passed in 0.33s ==============================
```

---

## ☁️ Deployment Instructions & Ephemeral Storage Notice

### Deploying with Gunicorn
The project contains a production-ready `Procfile`:
```
web: gunicorn app:app
```

### Render Deployment Configuration
The `render.yaml` file configures the web service on Render:
- **Build Command:** `pip install -r requirements.txt && python seed.py`
- **Start Command:** `gunicorn app:app`

### ⚠️ Ephemeral Storage vs. Persistent Disks
- On free-tier cloud instances (such as Render Free Tier or standard containers), the local disk filesystem is **ephemeral**. When the web service sleeps or is redeployed, local file changes (such as newly written SQLite database records) are reset to the initial repository state.
- **Production Solution:** To retain all quiz attempts permanently across cloud redeployments, configure a Render Persistent Disk volume (e.g. 1 GB disk mounted at `/var/data`) and set the environment variable:
  ```bash
  DATABASE_PATH=/var/data/quiz.db
  ```
  The application automatically reads `DATABASE_PATH` and connects to the persistent volume.

---

## 📊 Assignment Requirements Status

### Completed Requirements (Level 1):
- [x] Working full-stack web application with responsive UI.
- [x] Python Flask backend with RESTful API endpoints.
- [x] Connected SQLite database with relational schema.
- [x] 10 core Python multiple-choice questions stored in SQLite.
- [x] Client questions retrieved dynamically via `fetch('/api/questions')`.
- [x] Answers validated authoritatively on the backend.
- [x] Server-side calculation of score, percentage, and grade.
- [x] Persistence of quiz attempts and itemized student responses in SQLite.
- [x] Post-submission review displaying student choice, correct choice, and explanations.
- [x] Dedicated Start Quiz button, single-question flow, and 15-minute countdown timer.
- [x] Duplicate submission prevention and accidental submission validation.
- [x] Automated pytest suite covering 13 test cases.
- [x] Comprehensive documentation and setup instructions.

### Future Enhancements / Unimplemented Scope (Level 2 & 3):
- **Adaptive Question Selection:** Currently, all 10 questions are delivered sequentially. Dynamic branching based on item response theory (IRT) or dynamic difficulty adjustment is reserved for Level 2.
- **User Authentication & Accounts:** Currently, student names are input at quiz start. User login, password hashing, and OAuth are planned for future levels.
- **AI Recommendation Engine:** No external LLM or AI chatbot has been artificially added; all explanations are grounded in verified Python pedagogical principles stored in the database.

---

## 🤖 AI Assistance Disclosure
In accordance with internship evaluation transparency standards: AI coding assistance was utilized during this project to help diagnose architectural bugs in the original submission, design normalized SQLite relational schemas, construct comprehensive pytest test cases, and refine the front-end user experience. All generated code was thoroughly tested, verified, and debugged in a real Linux runtime environment.
