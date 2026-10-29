DIGIT Innovations Internship Project Report

Candidate Name: AkshayaProject Title: Smart Adaptive Learning Application (Python Core Assessment Engine)Assignment Track: Level 1 Mandatory Implementation (100% Tested & Verified)Submission Date: October 29, 2026Live Application URL: https://ais-pre-p67ax6eq33qolvrmngkczb-989727123617.asia-east1.run.app

1. Executive Summary & Problem Diagnosis

The initial submission for the Python Quiz Application had several architectural flaws, data synchronization issues, and missing mandatory Level 1 features:

1. Dual/Conflicting Data Stores: app.py contained a hardcoded Python list of questions, while templates/index.html maintained a separate JavaScript question array.2. Client-Side Answer Leak: The HTML markup contained correct answers (correctIndex) and explanations in the client-side JavaScript, exposing them before submission.3. Missing SQLite Database: The Level 1 compulsory requirement of persistent SQLite storage was completely absent.4. Disconnected Architecture: The frontend calculated the final score client-side and never actually called the Flask backend.5. Timer and Validation Flaws: The countdown timer started immediately upon page load rather than upon clicking Start Quiz, and accidental submissions were not prevented.6. Missing Automated Tests: No automated tests existed.

2. Implemented Architecture (3-Tier Model)

The application was restructured into a robust 3-tier production architecture:- Data Tier (SQLite): Single source of truth with relational tables for questions, quiz_attempts, and student_responses.- Application Tier (Flask 3.0): RESTful endpoints for question fetching (omitting answer key), authoritative answer evaluation, attempt recording, and history retrieval.- Presentation Tier (HTML/CSS/JS): Clean responsive interface with Start Screen, single-question presentation, 15:00 countdown timer, and comprehensive post-submission review.

3. Database Schema Specification

Table Name

Key Columns

Description & Purpose

questions

id, topic, difficulty, question, code_snippet, option_a, option_b, option_c, option_d, correct_index, explanation, hint

Authoritative question bank with 10 core Python MCQs and explanations.

quiz_attempts

id, attempt_uuid, student_name, total_questions, correct_answers, incorrect_answers, score, percentage, grade, passed, time_taken_seconds, created_at

Persists every completed quiz attempt with scores, percentage ratings, and audit timestamps.

student_responses

id, attempt_id (FK), question_id (FK), selected_index, is_correct, created_at

Maintains itemized records of each student response per attempt for diagnostics.

4. Automated Test Suite Results (pytest)

13 automated tests were created in tests/test_quiz.py and executed against isolated temporary SQLite databases. All 13 tests passed successfully:

✔ test_flask_app_initialization (PASSED)✔ test_database_initialization_and_schema (PASSED)✔ test_retrieval_of_questions_from_sqlite (PASSED)✔ test_availability_of_at_least_10_questions (PASSED)✔ test_client_questions_endpoint_does_not_leak_answers (PASSED)✔ test_correct_answer_evaluation (PASSED)✔ test_incorrect_answer_evaluation (PASSED)✔ test_mixed_answers_score_and_percentage_calculation (PASSED)✔ test_invalid_submission_handling (PASSED)✔ test_saving_quiz_attempts_and_answers_in_sqlite (PASSED)✔ test_retrieving_previously_saved_results (PASSED)✔ test_restart_persistence_across_connections (PASSED)✔ test_duplicate_submission_handling (PASSED)

5. Local Execution Instructions

1. Install dependencies: pip install -r requirements.txt2. Seed SQLite database: python seed.py3. Start Flask web server: python app.py (Open http://127.0.0.1:5000)4. Run automated test suite: pytest -v tests/test_quiz.py

Candidate Signature: AkshayaSubmission Date: October 29, 2026