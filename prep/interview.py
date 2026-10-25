import json, random
from pathlib import Path
from datetime import datetime
import re
import shutil

PREP_DIR = Path(__file__).parent
ARCHIVE_DIR = PREP_DIR / "archive"
DETAILS_FILE = PREP_DIR / "interview_details.txt"
STARTER_FILE = PREP_DIR / "questions.starter.json"
QUESTIONS_FILE = Path(__file__).parent/"questions.json"
ANSWERS_FILE = Path(__file__).parent/"answers.json"
COACH_NOTES_FILE = Path(__file__).parent / "coach_notes.md"

def load_questions(path: Path = QUESTIONS_FILE) -> list[dict]:
    """Load the question bank; fall back to the starter bank if it doesn't exist yet."""
    if not path.exists():
        path = STARTER_FILE
    return json.loads(path.read_text(encoding="utf-8"))

def load_answers(path=ANSWERS_FILE) -> list[dict]:
    """Load the file containing the answers to the questions ansked.
    Return empty list of file not created yet."""
    if not path.exists():
        return []
    answers = json.loads(path.read_text(encoding="utf-8"))
    return answers

def list_topics(questions: list[dict]) -> set[str]:
    """Find list of unique topics and return as a set."""
    return {item.get("topic") for item in questions}

def topic_stats(answers: list[dict]) -> dict[str, dict]:
    """Return count, average score and average time taken in seconds
    per topic, skipping unscored/untimed answers."""
    avgs = {}
    for record in answers:
        topic = record.get("topic")
        score = record.get("score")
        second = record.get("seconds")
        if topic is None or score is None:
            continue
        if topic not in avgs:
            avgs[topic] = {"scores": [], "seconds": []}
        avgs[topic]["scores"].append(score)
        if second is not None:
            avgs[topic]["seconds"].append(second)

    return {
        topic: {
            "count": len(s["scores"]), 
            "avg_score": round(sum(s["scores"]) / len(s["scores"]), 1), 
            "avg_time": round(sum(s["seconds"]) / len(s["seconds"])) if len(s["seconds"]) != 0 else None,
        }
        for topic, s in avgs.items()
    }

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

def save_answer(question: dict, answer: str, score: int | None=None, seconds: int | None=None, path: Path=ANSWERS_FILE) -> None:
    """Saves the picked question and its answer as a list of dicts in answer file,
    creates it as well if not there."""
    if path.exists() :
        answers = json.loads(path.read_text(encoding="utf-8"))
    else:
        answers = []
    answers.append({"topic": question["topic"], "question": question["question"], "answer": answer, "score": score, "seconds": seconds})
    path.write_text(json.dumps(answers, indent=2), encoding="utf-8")

def save_coaching(question: str, answer: str, coaching: str, path: Path = COACH_NOTES_FILE) -> None:
    """Append one coaching entry to the coach notes file, creating it if needed."""
    entry = f"""
    # {question}
    *{datetime.now():%Y-%m-%d %H:%M}*

    **Your answer:** {answer}

    {coaching}

    ---
    """
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry)

def company_name(details: str) -> str:
    """Return a folder-safe company name from the line after '# Interview'."""
    lines = details.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower() == "# interview" and i + 1 < len(lines):
            name = lines[i + 1].split(",")[0].strip()
            safe = re.sub(r'[\\/:*?"<>|]', "", name).replace(" ", "_")
            return safe or "interview"
    return "interview"

def next_free_folder(base: Path, name: str) -> Path:
    """Return base/name, or base/name_2, name_3... if it already exists."""
    folder = base / name
    n = 2
    while folder.exists():
        folder = base / f"{name}_{n}"
        n += 1
    return folder

def archive_current_interview() -> Path | None:
    """Move the current interview's files to archive/<company>/ and reset the bank.

    Returns the archive folder, or None if there was no interview to archive.
    """
    if not DETAILS_FILE.exists():
        return None
    name = company_name(DETAILS_FILE.read_text(encoding="utf-8"))
    folder = next_free_folder(ARCHIVE_DIR, name)
    folder.mkdir(parents=True)
    for f in [DETAILS_FILE, QUESTIONS_FILE, ANSWERS_FILE, COACH_NOTES_FILE]:
        if f.exists():
            shutil.move(f, folder / f.name)
    shutil.copy(STARTER_FILE, QUESTIONS_FILE)
    return folder

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