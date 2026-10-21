import json, random
from pathlib import Path

QUESTIONS_FILE = Path(__file__).parent/"questions.json"
ANSWERS_FILE = Path(__file__).parent/"answers.json"

def load_questions(path: Path=QUESTIONS_FILE) -> list[dict]:
    """Load the question bank from a JSON file and return it as a list of dicts."""
    questions = json.loads(path.read_text(encoding="utf-8"))
    return questions

def list_topics(questions: list[dict]) -> set[str]:
    """Find list of unique topics and return as a set."""
    return {item.get("topic") for item in questions}

def pick_question(questions: list[dict], topic: str | None=None) -> dict:
    """Pick a question from the question bank from any 
    topic by default or specific to topic if mentioned"""
    if topic is not None:
        filtered_questions = [item for item in questions if item.get("topic") == topic]
        return random.choice(filtered_questions)
    return random.choice(questions)

def add_question(topic: str, question: str, path: Path = QUESTIONS_FILE) -> None:
    """Saves the picked/generated question and its topic as dict in question file
    if its not present already."""
    if path.exists() :
            questions = json.loads(path.read_text(encoding="utf-8"))
            if {"topic": topic, "question": question} in questions:
                return
    else:
        questions = []
    questions.append({"topic": topic, "question": question})
    path.write_text(json.dumps(questions, indent=2), encoding="utf-8")

def save_answer(question: dict, answer: str, path: Path=ANSWERS_FILE) -> None:
    """Saves the picked question and its answer as a list of dicts in answer file,
    creates it as well if not there."""
    if path.exists() :
        answers = json.loads(path.read_text(encoding="utf-8"))
    else:
        answers = []
    answers.append({"topic": question["topic"], "question": question["question"], "answer": answer})
    path.write_text(json.dumps(answers, indent=2), encoding="utf-8")

def main() :
    """Runs the full interview pipeline."""
    questions = load_questions()
    print("Available topics :")
    topics = sorted(list_topics(questions))
    for i in topics :
        print(i)
    topic = input("Enter preferred topic if any : ")
    if topic == "" or topic not in topics:
        topic = None
        print("Chosen topic not available -> Choosing a random topic.")
    else:
        print("Chosen topic :", topic)
    picked_question = pick_question(questions, topic)
    print("Picked Question :", picked_question["question"])
    answer = input("Enter your answer : ")
    save_answer(picked_question, answer)
    print("Operation successful")

if __name__ == "__main__" :
    main()