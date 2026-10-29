-- SQLite Schema for Python Quiz Smart Learning Application
-- DIGIT Innovations Internship Assignment
-- Author: Akshaya

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'Medium',
    question TEXT NOT NULL,
    code_snippet TEXT,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_index INTEGER NOT NULL CHECK (correct_index BETWEEN 0 AND 3),
    explanation TEXT NOT NULL,
    hint TEXT
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_uuid TEXT UNIQUE NOT NULL,
    student_name TEXT DEFAULT 'Akshaya',
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    incorrect_answers INTEGER NOT NULL,
    score INTEGER NOT NULL,
    percentage REAL NOT NULL,
    grade TEXT NOT NULL,
    passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
    time_taken_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_index INTEGER,
    is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic);
CREATE INDEX IF NOT EXISTS idx_attempts_created ON quiz_attempts(created_at);
CREATE INDEX IF NOT EXISTS idx_responses_attempt ON student_responses(attempt_id);
