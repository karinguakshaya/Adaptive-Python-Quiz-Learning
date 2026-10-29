#!/usr/bin/env python3
"""
Seed Script for Python Quiz Application
Initializes the SQLite schema and seeds the 10 Python multiple-choice questions.

Usage:
    python seed.py
"""

import sys
from database import init_db, seed_questions, DEFAULT_DB_PATH, get_all_questions_admin

def main():
    print(f"Initializing database at: {DEFAULT_DB_PATH}")
    init_db()
    count = seed_questions()
    print(f"Database successfully initialized and seeded with {count} questions.")
    
    # Verify seeded questions
    questions = get_all_questions_admin()
    print(f"Verification: Found {len(questions)} questions in SQLite database:")
    for qid, q in questions.items():
        print(f"  [{q['id']}] ({q['topic']} - {q['difficulty']}) {q['question'][:60]}...")
    
    print("\nDatabase is ready for quiz attempts!")

if __name__ == "__main__":
    main()
