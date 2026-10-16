import json

from prep.interview import load_questions, pick_question, save_answer

QUESTIONS = [
    {"topic": "agents", "question": "What is an agent?"},
    {"topic": "nanda", "question": "What is a registry?"},
]


def test_load_questions_reads_the_real_file():
    questions = load_questions()
    assert len(questions) > 0
    assert "question" in questions[0]


def test_pick_question_filters_by_topic():
    for _ in range(10):
        assert pick_question(QUESTIONS, "nanda")["topic"] == "nanda"


def test_pick_question_without_topic_picks_any():
    assert pick_question(QUESTIONS) in QUESTIONS


def test_save_answer_appends(tmp_path):
    path = tmp_path / "answers.json"  # a temporary file, so the real one is untouched

    save_answer(QUESTIONS[0], "An LLM in a tool loop", path)
    save_answer(QUESTIONS[1], "A phone book for agents", path)

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == [
        {"question": "What is an agent?", "answer": "An LLM in a tool loop"},
        {"question": "What is a registry?", "answer": "A phone book for agents"},
    ]