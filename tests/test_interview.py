import json
import prep.interview as p
from pathlib import Path

QUESTIONS = [
    {"topic": "agents", "question": "What is an agent?"},
    {"topic": "nanda", "question": "What is a registry?"},
]


def test_load_questions_reads_the_real_file():
    questions = p.load_questions()
    assert len(questions) > 0
    assert "question" in questions[0]

def test_list_topics():
    QUESTIONS1 = [
        {"topic": "agents", "question": "What is an agent?"},
        {"topic": "nanda", "question": "What is a registry?"},
        {"topic": "nanda", "question": "What is nandatown?"},
    ]
    topics1 = p.list_topics(QUESTIONS1)
    assert not len(QUESTIONS1) == len(topics1)
    topics = p.list_topics(QUESTIONS)
    assert len(QUESTIONS) == len(topics)

def test_topic_stats():
    ANSWERS = [
        {"topic": "agents", "question": "What is an agent?", "score": 5},
        {"topic": "agents", "question": "What is A2A system?", "score": 1},
        {"topic": "nanda", "question": "What is a registry?", "score": 8},
        {"topic": "nanda", "question": "What is nandatown?"},
    ]
    stats = p.topic_stats(ANSWERS)
    assert stats == {
        "agents": {"count": 2, "avg_score": 3.0},
        "nanda": {"count": 1, "avg_score": 8.0}
    }
    
def test_pick_question_filters_by_topic():
    for _ in range(10):
        assert p.pick_question(QUESTIONS, "nanda")["topic"] == "nanda"


def test_pick_question_without_topic_picks_any():
    assert p.pick_question(QUESTIONS) in QUESTIONS

def test_add_question_unique(tmp_path):
    path = tmp_path / "questions.json"
    p.add_question("random", "Is the test working?", path)
    p.add_question("random", "Is the test really working?", path)
    added = json.loads(path.read_text(encoding="utf-8"))
    assert added == [
        {"topic": "random", "question": "Is the test working?"},
        {"topic": "random", "question": "Is the test really working?"},
    ]

def test_add_question_duplicates(tmp_path):
    path = tmp_path / "questions.json"
    p.add_question("random", "Is the test working?", path)
    p.add_question("random", "Is the test working?", path)
    added = json.loads(path.read_text(encoding="utf-8"))
    assert added == [
        {"topic": "random", "question": "Is the test working?"},
    ]

def test_save_answer_appends(tmp_path):
    path = tmp_path / "answers.json"  # a temporary file, so the real one is untouched
    p.save_answer(QUESTIONS[0], "An LLM in a tool loop", 5, path)
    p.save_answer(QUESTIONS[1], "A phone book for agents", 6, path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == [
        {"topic": "agents", "question": "What is an agent?", "answer": "An LLM in a tool loop", "score": 5},
        {"topic": "nanda", "question": "What is a registry?", "answer": "A phone book for agents", "score": 6},
    ]