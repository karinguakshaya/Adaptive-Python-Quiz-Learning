"""
Automated Pytest Suite for Python Quiz Application
DIGIT Innovations Internship Project

Covers:
1. Flask application initialization
2. Database initialization and schema creation
3. Retrieval of questions from SQLite
4. Availability of at least 10 questions in SQLite
5. Verification that client questions endpoint does not leak correct answers or explanations
6. Correct answer evaluation (100% score)
7. Incorrect answer evaluation (0% score)
8. Mixed correct and incorrect answers evaluation (e.g., 60% score)
9. Score and percentage calculation accuracy
10. Invalid and malformed submissions handling (400 responses)
11. Saving quiz attempts and student responses into SQLite
12. Retrieving previously saved results from SQLite
13. Persistence across simulated restarts (re-opening the SQLite database file)
14. Duplicate submission prevention (submitting same attemptUuid rejected with 409)
"""

import os
import tempfile
import uuid
import pytest

import database
from app import app


@pytest.fixture
def temp_db():
    """Creates an isolated temporary SQLite database file for each test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database.init_db(path)
    database.seed_questions(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def client(temp_db, monkeypatch):
    """Configures the Flask test client with an isolated temporary SQLite database."""
    monkeypatch.setattr(database, "DEFAULT_DB_PATH", temp_db)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_flask_app_initialization(client):
    """Test 1: Flask application initializes and responds to root and health routes."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "SQLite"
    assert data["total_questions_in_db"] >= 10


def test_database_initialization_and_schema(temp_db):
    """Test 2: Database schema initializes tables: questions, quiz_attempts, student_responses."""
    conn = database.get_db_connection(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row["name"] for row in cursor.fetchall()}
    conn.close()

    assert "questions" in tables
    assert "quiz_attempts" in tables
    assert "student_responses" in tables


def test_retrieval_of_questions_from_sqlite(temp_db):
    """Test 3: Verify questions can be retrieved directly from the SQLite database."""
    questions = database.get_client_questions(temp_db)
    assert isinstance(questions, list)
    assert len(questions) >= 10
    first_q = questions[0]
    assert "question" in first_q
    assert "options" in first_q
    assert len(first_q["options"]) == 4


def test_availability_of_at_least_10_questions(client):
    """Test 4: Verify the /api/questions endpoint returns at least 10 questions."""
    resp = client.get("/api/questions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["total"] >= 10
    assert len(data["questions"]) >= 10


def test_client_questions_endpoint_does_not_leak_answers(client):
    """Test 5: Ensure correct answers and explanations are NEVER exposed to the frontend before submission."""
    resp = client.get("/api/questions")
    data = resp.get_json()
    for q in data["questions"]:
        assert "correct_index" not in q
        assert "correctIndex" not in q
        assert "explanation" not in q


def test_correct_answer_evaluation(client, temp_db):
    """Test 6: Perfect score evaluation - all answers correct yield 100% and grade A+."""
    admin_questions = database.get_all_questions_admin(temp_db)
    correct_answers = {str(qid): q["correctIndex"] for qid, q in admin_questions.items()}

    attempt_uuid = str(uuid.uuid4())
    payload = {
        "attemptUuid": attempt_uuid,
        "studentName": "Akshaya Test",
        "timeTakenSeconds": 180,
        "answers": correct_answers
    }

    resp = client.post("/api/submit", json=payload)
    assert resp.status_code == 200
    res_data = resp.get_json()

    assert res_data["status"] == "success"
    assert res_data["score"] == len(admin_questions)
    assert res_data["total"] == len(admin_questions)
    assert res_data["percentage"] == 100.0
    assert "A+" in res_data["grade"]
    assert res_data["passed"] is True
    assert res_data["incorrectAnswers"] == 0

    # Ensure all individual questions are marked correct
    for item in res_data["results"]:
        assert item["isCorrect"] is True
        assert item["userChoice"] == item["correctChoice"]
        assert len(item["explanation"]) > 0


def test_incorrect_answer_evaluation(client, temp_db):
    """Test 7: Zero score evaluation - all wrong answers yield 0% and grade D."""
    admin_questions = database.get_all_questions_admin(temp_db)
    wrong_answers = {}
    for qid, q in admin_questions.items():
        # Choose any option that is NOT the correct one
        wrong_idx = (q["correctIndex"] + 1) % 4
        wrong_answers[str(qid)] = wrong_idx

    attempt_uuid = str(uuid.uuid4())
    payload = {
        "attemptUuid": attempt_uuid,
        "studentName": "Akshaya Test",
        "timeTakenSeconds": 120,
        "answers": wrong_answers
    }

    resp = client.post("/api/submit", json=payload)
    assert resp.status_code == 200
    res_data = resp.get_json()

    assert res_data["score"] == 0
    assert res_data["percentage"] == 0.0
    assert "D" in res_data["grade"]
    assert res_data["passed"] is False
    assert res_data["incorrectAnswers"] == len(admin_questions)

    for item in res_data["results"]:
        assert item["isCorrect"] is False
        assert item["userChoice"] != item["correctChoice"]


def test_mixed_answers_score_and_percentage_calculation(client, temp_db):
    """Test 8: Mixed answers - exactly 6 out of 10 correct produces 60% and grade B."""
    admin_questions = database.get_all_questions_admin(temp_db)
    mixed_answers = {}
    for i, (qid, q) in enumerate(sorted(admin_questions.items())):
        if i < 6:
            mixed_answers[str(qid)] = q["correctIndex"]  # Correct
        else:
            mixed_answers[str(qid)] = (q["correctIndex"] + 1) % 4  # Incorrect

    resp = client.post("/api/submit", json={
        "attemptUuid": str(uuid.uuid4()),
        "studentName": "Akshaya",
        "timeTakenSeconds": 240,
        "answers": mixed_answers
    })
    assert resp.status_code == 200
    res = resp.get_json()

    assert res["score"] == 6
    assert res["total"] == 10
    assert res["percentage"] == 60.0
    assert "B" in res["grade"]
    assert res["passed"] is True
    assert res["correctAnswers"] == 6
    assert res["incorrectAnswers"] == 4


def test_invalid_submission_handling(client):
    """Test 9: Invalid submissions (empty payload, missing answers, non-JSON) return 400 Bad Request."""
    # Not JSON
    resp1 = client.post("/api/submit", data="Not JSON", content_type="text/plain")
    assert resp1.status_code == 400

    # Missing answers dict
    resp2 = client.post("/api/submit", json={"studentName": "Test"})
    assert resp2.status_code == 400

    # Answers is a string instead of dict
    resp3 = client.post("/api/submit", json={"answers": "invalid"})
    assert resp3.status_code == 400


def test_saving_quiz_attempts_and_answers_in_sqlite(client, temp_db):
    """Test 10: Quiz submission inserts record into quiz_attempts and 10 rows into student_responses."""
    attempt_uuid = str(uuid.uuid4())
    resp = client.post("/api/submit", json={
        "attemptUuid": attempt_uuid,
        "studentName": "Akshaya Persistence",
        "timeTakenSeconds": 300,
        "answers": {"1": 0, "2": 3}
    })
    assert resp.status_code == 200

    conn = database.get_db_connection(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_attempts WHERE attempt_uuid = ?", (attempt_uuid,))
    attempt_row = cursor.fetchone()
    assert attempt_row is not None
    assert attempt_row["student_name"] == "Akshaya Persistence"

    cursor.execute("SELECT COUNT(*) AS cnt FROM student_responses WHERE attempt_id = ?", (attempt_row["id"],))
    count = cursor.fetchone()["cnt"]
    assert count == 10  # All 10 questions evaluated and stored
    conn.close()


def test_retrieving_previously_saved_results(client):
    """Test 11: Saved quiz attempts can be retrieved via /api/attempts and /api/attempts/<uuid>."""
    test_uuid = str(uuid.uuid4())
    client.post("/api/submit", json={
        "attemptUuid": test_uuid,
        "studentName": "Akshaya Review",
        "timeTakenSeconds": 95,
        "answers": {"1": 0}
    })

    # Retrieve all attempts
    list_resp = client.get("/api/attempts")
    assert list_resp.status_code == 200
    list_data = list_resp.get_json()
    uuids = [att["attempt_uuid"] for att in list_data["attempts"]]
    assert test_uuid in uuids

    # Retrieve specific attempt details
    detail_resp = client.get(f"/api/attempts/{test_uuid}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.get_json()
    assert detail_data["attempt"]["attempt_uuid"] == test_uuid
    assert len(detail_data["attempt"]["responses"]) == 10


def test_restart_persistence_across_connections(temp_db):
    """Test 12: Simulates backend restart. Data in SQLite persists across connection closures and re-opens."""
    test_uuid = str(uuid.uuid4())
    database.save_quiz_attempt(
        attempt_uuid=test_uuid,
        student_name="Akshaya Restart Test",
        total_questions=10,
        correct_answers=7,
        incorrect_answers=3,
        score=7,
        percentage=70.0,
        grade="B (Good)",
        passed=True,
        time_taken_seconds=210,
        student_responses_list=[{"question_id": 1, "selected_index": 0, "is_correct": True}],
        db_path=temp_db
    )

    # Reconnect fresh to SQLite database file
    reopened = database.get_attempt_by_uuid(test_uuid, db_path=temp_db)
    assert reopened is not None
    assert reopened["student_name"] == "Akshaya Restart Test"
    assert reopened["score"] == 7
    assert reopened["percentage"] == 70.0


def test_duplicate_submission_handling(client):
    """Test 13: Submitting the same attemptUuid twice is rejected with HTTP 409 Conflict."""
    attempt_uuid = str(uuid.uuid4())
    payload = {
        "attemptUuid": attempt_uuid,
        "studentName": "Akshaya Duplicate Test",
        "timeTakenSeconds": 150,
        "answers": {"1": 0, "2": 3}
    }

    # First submission -> 200 OK
    resp1 = client.post("/api/submit", json=payload)
    assert resp1.status_code == 200

    # Second submission with exact same attemptUuid -> 409 Conflict
    resp2 = client.post("/api/submit", json=payload)
    assert resp2.status_code == 409
    data2 = resp2.get_json()
    assert data2["code"] == "DUPLICATE_SUBMISSION"
