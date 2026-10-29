"""
Python Quiz Application - Flask Backend Server
DIGIT Innovations Internship Assignment Submission
Candidate: Akshaya

Features:
- Single authoritative data source: SQLite Database.
- Backend answer validation and score calculation.
- Complete attempt and response persistence in SQLite.
- Secure API endpoints (does not leak answer key to frontend).
- Duplicate submission prevention.
- Detailed question review with explanations after submission.
"""

import os
import uuid
from flask import Flask, jsonify, request, render_template, send_from_directory, send_file
from flask_cors import CORS

import database

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Ensure database is created and seeded upon application startup
with app.app_context():
    database.init_db()
    database.seed_questions()


@app.route("/")
def home():
    """Serves the main quiz web interface."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Returns application health and database record statistics."""
    try:
        questions = database.get_client_questions()
        attempts = database.get_attempts(limit=5)
        return jsonify({
            "status": "healthy",
            "candidate": "Akshaya",
            "project": "Python Smart Learning Quiz",
            "database": "SQLite",
            "total_questions_in_db": len(questions),
            "total_recorded_attempts": len(attempts)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/questions", methods=["GET"])
def get_questions():
    """
    Retrieves all quiz questions from the SQLite database.
    Omit correct_index and explanation to prevent client-side inspection.
    """
    try:
        questions = database.get_client_questions()
        return jsonify({
            "status": "success",
            "total": len(questions),
            "questions": questions
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve questions from database: {str(e)}"
        }), 500


@app.route("/api/submit", methods=["POST"])
def submit_quiz():
    """
    Authoritative backend quiz evaluation.
    - Validates student responses against SQLite question records.
    - Calculates score, percentage, grade, and pass status.
    - Persists attempt and itemized student responses in SQLite.
    - Prevents duplicate submissions.
    - Returns detailed review including explanations.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid request body. Expected JSON object."
        }), 400

    answers = payload.get("answers")
    if not isinstance(answers, dict):
        return jsonify({
            "status": "error",
            "message": "Missing or invalid 'answers' payload. Expected key-value mapping of question ID to choice index."
        }), 400

    attempt_uuid = payload.get("attemptUuid") or str(uuid.uuid4())
    student_name = payload.get("studentName", "Akshaya")
    time_taken_seconds = int(payload.get("timeTakenSeconds", 0))

    # Retrieve authoritative question bank from SQLite
    try:
        questions_db = database.get_all_questions_admin()
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database error while fetching question bank: {str(e)}"
        }), 500

    if not questions_db:
        return jsonify({
            "status": "error",
            "message": "No questions found in database. Please seed the database."
        }), 500

    score = 0
    total = len(questions_db)
    results = []
    responses_to_save = []

    for q_id, q_data in sorted(questions_db.items()):
        # Handle string or int keys
        user_choice = answers.get(str(q_id))
        if user_choice is None:
            user_choice = answers.get(q_id)

        # Validate that choice is an integer between 0 and 3, or None if unanswered
        valid_choice = None
        if user_choice is not None:
            try:
                parsed_choice = int(user_choice)
                if 0 <= parsed_choice < len(q_data["options"]):
                    valid_choice = parsed_choice
            except (ValueError, TypeError):
                valid_choice = None

        is_correct = (valid_choice is not None and valid_choice == q_data["correctIndex"])
        if is_correct:
            score += 1

        results.append({
            "questionId": q_id,
            "topic": q_data["topic"],
            "difficulty": q_data["difficulty"],
            "question": q_data["question"],
            "codeSnippet": q_data["codeSnippet"],
            "options": q_data["options"],
            "userChoice": valid_choice,
            "correctChoice": q_data["correctIndex"],
            "isCorrect": is_correct,
            "explanation": q_data["explanation"]
        })

        responses_to_save.append({
            "question_id": q_id,
            "selected_index": valid_choice,
            "is_correct": is_correct
        })

    percentage = round((score / total) * 100, 2)

    # Grading classification
    if percentage >= 90:
        grade = "A+ (Outstanding)"
    elif percentage >= 80:
        grade = "A (Excellent)"
    elif percentage >= 60:
        grade = "B (Good)"
    elif percentage >= 40:
        grade = "C (Satisfactory)"
    else:
        grade = "D (Needs Improvement)"

    passed = bool(percentage >= 60)
    incorrect_answers = total - score

    # Save to SQLite database
    try:
        attempt_id = database.save_quiz_attempt(
            attempt_uuid=attempt_uuid,
            student_name=student_name,
            total_questions=total,
            correct_answers=score,
            incorrect_answers=incorrect_answers,
            score=score,
            percentage=percentage,
            grade=grade,
            passed=passed,
            time_taken_seconds=time_taken_seconds,
            student_responses_list=responses_to_save
        )
    except ValueError as e:
        # Duplicate submission detected
        return jsonify({
            "status": "error",
            "code": "DUPLICATE_SUBMISSION",
            "message": str(e)
        }), 409
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to persist quiz results to database: {str(e)}"
        }), 500

    return jsonify({
        "status": "success",
        "attemptId": attempt_id,
        "attemptUuid": attempt_uuid,
        "studentName": student_name,
        "score": score,
        "total": total,
        "correctAnswers": score,
        "incorrectAnswers": incorrect_answers,
        "percentage": percentage,
        "grade": grade,
        "passed": passed,
        "timeTakenSeconds": time_taken_seconds,
        "results": results
    }), 200


@app.route("/api/attempts", methods=["GET"])
def get_attempts():
    """Retrieves previous quiz attempts from SQLite database."""
    try:
        limit = request.args.get("limit", 20, type=int)
        attempts = database.get_attempts(limit=limit)
        return jsonify({
            "status": "success",
            "count": len(attempts),
            "attempts": attempts
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch attempts: {str(e)}"
        }), 500


@app.route("/api/attempts/<attempt_uuid>", methods=["GET"])
def get_attempt_detail(attempt_uuid: str):
    """Retrieves details of a specific attempt with all responses."""
    try:
        detail = database.get_attempt_by_uuid(attempt_uuid)
        if not detail:
            return jsonify({
                "status": "error",
                "message": f"Attempt '{attempt_uuid}' not found."
            }), 404
        return jsonify({
            "status": "success",
            "attempt": detail
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch attempt details: {str(e)}"
        }), 500


@app.route("/api/download/zip", methods=["GET"])
def download_zip():
    """Provides direct download for the fixed submission ZIP file."""
    zip_path = os.path.join(os.path.dirname(__file__), "Python_Quiz_Internship_Submission_Akshaya_Fixed.zip")
    if not os.path.exists(zip_path):
        return jsonify({"status": "error", "message": "ZIP file not found."}), 404
    return send_file(
        zip_path,
        as_attachment=True,
        download_name="Python_Quiz_Internship_Submission_Akshaya_Fixed.zip",
        mimetype="application/zip"
    )


@app.route("/api/download/docx", methods=["GET"])
def download_docx():
    """Provides direct download for the genuine Word (.docx) internship report."""
    docx_path = os.path.join(os.path.dirname(__file__), "INTERNSHIP_REPORT.docx")
    if not os.path.exists(docx_path):
        return jsonify({"status": "error", "message": "Report file not found."}), 404
    return send_file(
        docx_path,
        as_attachment=True,
        download_name="INTERNSHIP_REPORT.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.route("/api/download/doc", methods=["GET"])
def download_doc():
    """Provides direct download for INTERNSHIP_REPORT.doc."""
    doc_path = os.path.join(os.path.dirname(__file__), "INTERNSHIP_REPORT.doc")
    if not os.path.exists(doc_path):
        return jsonify({"status": "error", "message": "Report file not found."}), 404
    return send_file(
        doc_path,
        as_attachment=True,
        download_name="INTERNSHIP_REPORT.doc",
        mimetype="application/msword"
    )


@app.route("/api/source-code", methods=["GET"])
def get_source_code():
    """Returns the code of all project files for in-browser inspection."""
    file_list = [
        "app.py",
        "database.py",
        "schema.sql",
        "seed.py",
        "requirements.txt",
        "Procfile",
        "render.yaml",
        "templates/index.html",
        "tests/test_quiz.py",
        "README.md",
        "SUBMISSION_URL.txt"
    ]
    result = {}
    base_dir = os.path.dirname(__file__)
    for fname in file_list:
        full_path = os.path.join(base_dir, fname)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    result[fname] = f.read()
            except Exception as e:
                result[fname] = f"Error reading file: {str(e)}"
    return jsonify({"status": "success", "files": result}), 200


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "API endpoint not found"}), 404
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
