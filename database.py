"""
Database Module for Python Quiz Application
Provides SQLite connection management, schema initialization, seed data,
and queries for questions, quiz attempts, and student responses.
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "quiz.db"))

INITIAL_QUESTIONS = [
    {
        "id": 1,
        "topic": "Variables",
        "difficulty": "Easy",
        "question": "What is the value of x and y after executing the following multiple variable assignment?",
        "code_snippet": "x, y = 15, 30\nx, y = y, x + y",
        "options": [
            "x = 30, y = 45",
            "x = 15, y = 45",
            "x = 30, y = 30",
            "SyntaxError: cannot assign simultaneously"
        ],
        "correct_index": 0,
        "explanation": "In Python, the right-hand side expressions are evaluated first from left to right as a tuple before any assignment occurs: (y, x + y) evaluates to (30, 45). Then, x is assigned 30 and y is assigned 45.",
        "hint": "Remember that Python evaluates the right-hand side tuple first before binding variables."
    },
    {
        "id": 2,
        "topic": "Data Types",
        "difficulty": "Medium",
        "question": "Which of the following built-in Python data types is immutable (cannot be modified after creation)?",
        "code_snippet": "# Examining mutation attempts\nsample_a = [1, 2, 3]\nsample_b = {'a': 1, 'b': 2}\nsample_c = {1, 2, 3}\nsample_d = (1, 2, 3)",
        "options": [
            "List [1, 2, 3]",
            "Dictionary {'a': 1}",
            "Set {1, 2, 3}",
            "Tuple (1, 2, 3)"
        ],
        "correct_index": 3,
        "explanation": "Tuples, strings, integers, floats, and frozensets are immutable in Python. Lists, dictionaries, and sets are mutable. Modifying an element of a tuple raises a TypeError.",
        "hint": "Look for the sequence type defined with round parentheses () that does not support item assignment."
    },
    {
        "id": 3,
        "topic": "Operators",
        "difficulty": "Easy",
        "question": "What will be the output of the following arithmetic expressions involving Python operators?",
        "code_snippet": "result_1 = 19 // 4\nresult_2 = 2 ** 3 ** 2\nprint(result_1, result_2)",
        "options": [
            "4 64",
            "4 512",
            "4.75 64",
            "4.75 512"
        ],
        "correct_index": 1,
        "explanation": "The // operator performs floor division (19 // 4 is 4). The exponentiation operator ** has right-to-left associativity: 2 ** (3 ** 2) = 2 ** 9 = 512.",
        "hint": "Note that the power operator (**) evaluates from right to left, and // discards fractional parts."
    },
    {
        "id": 4,
        "topic": "Loops",
        "difficulty": "Medium",
        "question": "What is printed to the console when running this loop with an else clause?",
        "code_snippet": "numbers = [2, 4, 6, 8]\nfor n in numbers:\n    if n % 5 == 0:\n        print(\"Found multiple of 5\")\n        break\nelse:\n    print(\"No multiple found\")",
        "options": [
            "Found multiple of 5",
            "No multiple found",
            "Found multiple of 5 followed by No multiple found",
            "No output because loop exits normally"
        ],
        "correct_index": 1,
        "explanation": "In Python, a loop's else block executes only if the loop completes all iterations without encountering a break statement. Since none of the numbers are divisible by 5, the break never triggers, so the else clause runs.",
        "hint": "In Python, the loop else block runs only when the loop terminates naturally without a break."
    },
    {
        "id": 5,
        "topic": "Functions",
        "difficulty": "Hard",
        "question": "What does calling this function twice produce due to the default parameter behavior in Python?",
        "code_snippet": "def add_item(val, item_list=[]):\n    item_list.append(val)\n    return item_list\n\nfirst_call = add_item('Python')\nsecond_call = add_item('Flask')\nprint(second_call)",
        "options": [
            "['Flask']",
            "['Python', 'Flask']",
            "['Python']",
            "TypeError: item_list cannot be reused"
        ],
        "correct_index": 1,
        "explanation": "Default argument values in Python are evaluated once at function definition time, not at each call. Because item_list defaults to a mutable list [], the same list object is retained and mutated across subsequent calls.",
        "hint": "Default arguments are instantiated once when the function is defined, making mutable defaults persistent across calls."
    },
    {
        "id": 6,
        "topic": "Lists",
        "difficulty": "Medium",
        "question": "What is the output of the following list comprehension with step slicing?",
        "code_snippet": "data = [1, 2, 3, 4, 5, 6, 7, 8]\nsliced = data[1:7:2]\nreversed_comp = [x * 10 for x in sliced[::-1]]\nprint(reversed_comp)",
        "options": [
            "[60, 40, 20]",
            "[80, 60, 40, 20]",
            "[20, 40, 60]",
            "[70, 50, 30]"
        ],
        "correct_index": 0,
        "explanation": "data[1:7:2] takes elements from index 1 to 6 with a step of 2, producing [2, 4, 6]. Next, sliced[::-1] reverses this to [6, 4, 2]. The comprehension multiplies each by 10, producing [60, 40, 20].",
        "hint": "Break it into 3 steps: step slice index 1, 3, 5; then reverse with [::-1]; then multiply by 10."
    },
    {
        "id": 7,
        "topic": "OOP",
        "difficulty": "Medium",
        "question": "In Python Object-Oriented Programming, what is the role of the 'self' parameter in instance methods?",
        "code_snippet": "class Student:\n    def __init__(self, name, score):\n        self.name = name\n        self.score = score\n\n    def display(self):\n        return f\"{self.name}: {self.score}\"",
        "options": [
            "It represents the specific instance of the class upon which the method is called",
            "It is a global keyword required by the Python compiler for static methods",
            "It creates a duplicate copy of the class in system memory",
            "It is an optional variable that holds the class name"
        ],
        "correct_index": 0,
        "explanation": "'self' represents the specific instance of the class. It binds attributes and methods to the individual object instance upon which the method was called.",
        "hint": "Think about how instance attributes are bound to individual objects created from a class template."
    },
    {
        "id": 8,
        "topic": "OOP",
        "difficulty": "Hard",
        "question": "What will be the output when calling the get_info() method on an instance of Developer?",
        "code_snippet": "class Employee:\n    role = \"Staff\"\n    def __init__(self, name):\n        self.name = name\n\n    def get_info(self):\n        return f\"{self.name} - {self.role}\"\n\nclass Developer(Employee):\n    role = \"Software Engineer\"\n    def get_info(self):\n        parent_info = super().get_info()\n        return f\"Tech Dept: {parent_info}\"\n\ndev = Developer(\"Akshaya\")\nprint(dev.get_info())",
        "options": [
            "Tech Dept: Akshaya - Software Engineer",
            "Tech Dept: Akshaya - Staff",
            "Akshaya - Software Engineer",
            "AttributeError: super() cannot resolve role attribute"
        ],
        "correct_index": 0,
        "explanation": "super().get_info() calls the parent Employee method, but 'self' is still the Developer instance dev where 'role' is overridden as 'Software Engineer'. Hence it prints 'Tech Dept: Akshaya - Software Engineer'.",
        "hint": "Even when calling super(), self still points to the subclass instance where role is overridden."
    },
    {
        "id": 9,
        "topic": "OOP",
        "difficulty": "Medium",
        "question": "Which special dunder method is invoked when an object is passed to str() or print() for user-friendly string representation?",
        "code_snippet": "class Book:\n    def __init__(self, title, author):\n        self.title = title\n        self.author = author\n\n    # Which method goes here to format: \"Python Guide by Guido\"?\n    def ________(self):\n        return f\"{self.title} by {self.author}\"",
        "options": [
            "__str__(self)",
            "__repr__(self)",
            "__format__(self)",
            "__print__(self)"
        ],
        "correct_index": 0,
        "explanation": "The __str__() dunder method returns an informal, human-readable string representation of an object when passed to str() or print(). __repr__() is typically used for debugging.",
        "hint": "The method name matches the built-in function str() surrounded by double underscores."
    },
    {
        "id": 10,
        "topic": "Functions",
        "difficulty": "Medium",
        "question": "What is the output of the following function utilizing variable-length arguments (*args and **kwargs)?",
        "code_snippet": "def calculate_metrics(*args, **kwargs):\n    multiplier = kwargs.get('factor', 1)\n    return sum(args) * multiplier\n\nres1 = calculate_metrics(5, 10, 15)\nres2 = calculate_metrics(2, 3, factor=4)\nprint(res1, res2)",
        "options": [
            "30 20",
            "30 14",
            "0 20",
            "TypeError: invalid keyword argument"
        ],
        "correct_index": 0,
        "explanation": "*args packs positional arguments into a tuple (5, 10, 15 -> sum 30; factor=1 -> 30). **kwargs collects keyword arguments (2, 3 -> sum 5; factor=4 -> 20). The output is 30 20.",
        "hint": "*args packs positional parameters into a tuple, and kwargs.get('factor', 1) safely reads the optional multiplier."
    }
]


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection configured with Row factory."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the database schema using schema.sql."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.executescript(schema_sql)
    finally:
        conn.close()


def seed_questions(db_path: Optional[str] = None, questions: Optional[List[Dict[str, Any]]] = None) -> int:
    """
    Seeds questions into the database if the questions table is empty.
    Returns the count of seeded questions.
    """
    data = questions or INITIAL_QUESTIONS
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS cnt FROM questions")
            count = cursor.fetchone()["cnt"]
            if count == 0:
                for q in data:
                    opts = q["options"]
                    cursor.execute(
                        """
                        INSERT INTO questions (
                            id, topic, difficulty, question, code_snippet,
                            option_a, option_b, option_c, option_d,
                            correct_index, explanation, hint
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            q.get("id"),
                            q["topic"],
                            q.get("difficulty", "Medium"),
                            q["question"],
                            q.get("code_snippet"),
                            opts[0],
                            opts[1],
                            opts[2],
                            opts[3],
                            q["correct_index"],
                            q["explanation"],
                            q.get("hint")
                        )
                    )
                return len(data)
            return count
    finally:
        conn.close()


def get_client_questions(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all questions formatted for the frontend client.
    Crucially omits correct_index and explanation to prevent cheating.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, topic, difficulty, question, code_snippet,
                   option_a, option_b, option_c, option_d, hint
            FROM questions
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "topic": r["topic"],
                "difficulty": r["difficulty"],
                "question": r["question"],
                "codeSnippet": r["code_snippet"],
                "options": [r["option_a"], r["option_b"], r["option_c"], r["option_d"]],
                "hint": r["hint"]
            })
        return result
    finally:
        conn.close()


def get_all_questions_admin(db_path: Optional[str] = None) -> Dict[int, Dict[str, Any]]:
    """
    Retrieves all questions from the database with full answer key and explanations.
    Keyed by question ID for fast O(1) answer validation.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, topic, difficulty, question, code_snippet,
                   option_a, option_b, option_c, option_d,
                   correct_index, explanation, hint
            FROM questions
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        data = {}
        for r in rows:
            data[r["id"]] = {
                "id": r["id"],
                "topic": r["topic"],
                "difficulty": r["difficulty"],
                "question": r["question"],
                "codeSnippet": r["code_snippet"],
                "options": [r["option_a"], r["option_b"], r["option_c"], r["option_d"]],
                "correctIndex": r["correct_index"],
                "explanation": r["explanation"],
                "hint": r["hint"]
            }
        return data
    finally:
        conn.close()


def save_quiz_attempt(
    attempt_uuid: str,
    student_name: str,
    total_questions: int,
    correct_answers: int,
    incorrect_answers: int,
    score: int,
    percentage: float,
    grade: str,
    passed: bool,
    time_taken_seconds: int,
    student_responses_list: List[Dict[str, Any]],
    db_path: Optional[str] = None
) -> int:
    """
    Saves a completed quiz attempt and its individual responses inside a single database transaction.
    If an attempt with attempt_uuid already exists, raises ValueError to prevent duplicate submissions.
    Returns the generated attempt ID.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM quiz_attempts WHERE attempt_uuid = ?", (attempt_uuid,))
            existing = cursor.fetchone()
            if existing:
                raise ValueError(f"Attempt '{attempt_uuid}' has already been submitted.")

            cursor.execute(
                """
                INSERT INTO quiz_attempts (
                    attempt_uuid, student_name, total_questions,
                    correct_answers, incorrect_answers, score,
                    percentage, grade, passed, time_taken_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt_uuid,
                    student_name or "Akshaya",
                    total_questions,
                    correct_answers,
                    incorrect_answers,
                    score,
                    percentage,
                    grade,
                    1 if passed else 0,
                    time_taken_seconds
                )
            )
            attempt_id = cursor.lastrowid

            for resp in student_responses_list:
                cursor.execute(
                    """
                    INSERT INTO student_responses (
                        attempt_id, question_id, selected_index, is_correct
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        attempt_id,
                        resp["question_id"],
                        resp.get("selected_index"),
                        1 if resp["is_correct"] else 0
                    )
                )

            return attempt_id
    finally:
        conn.close()


def get_attempts(limit: int = 20, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves previous quiz attempts ordered by most recent."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, attempt_uuid, student_name, total_questions,
                   correct_answers, incorrect_answers, score, percentage,
                   grade, passed, time_taken_seconds, created_at
            FROM quiz_attempts
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_attempt_by_uuid(attempt_uuid: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves full details of a specific quiz attempt with itemized responses."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM quiz_attempts WHERE attempt_uuid = ?", (attempt_uuid,)
        )
        attempt_row = cursor.fetchone()
        if not attempt_row:
            return None

        attempt = dict(attempt_row)

        cursor.execute(
            """
            SELECT sr.question_id, sr.selected_index, sr.is_correct,
                   q.topic, q.difficulty, q.question, q.code_snippet,
                   q.option_a, q.option_b, q.option_c, q.option_d,
                   q.correct_index, q.explanation
            FROM student_responses sr
            JOIN questions q ON sr.question_id = q.id
            WHERE sr.attempt_id = ?
            ORDER BY sr.question_id ASC
            """,
            (attempt["id"],)
        )
        responses = []
        for r in cursor.fetchall():
            responses.append({
                "questionId": r["question_id"],
                "topic": r["topic"],
                "difficulty": r["difficulty"],
                "question": r["question"],
                "codeSnippet": r["code_snippet"],
                "options": [r["option_a"], r["option_b"], r["option_c"], r["option_d"]],
                "selectedChoice": r["selected_index"],
                "correctChoice": r["correct_index"],
                "isCorrect": bool(r["is_correct"]),
                "explanation": r["explanation"]
            })

        attempt["responses"] = responses
        return attempt
    finally:
        conn.close()
