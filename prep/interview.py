import json, random
from pathlib import Path

QUESTIONS_FILE = Path(__file__).parent/"questions.json"
ANSWERS_FILE = Path(__file__).parent/"answers.json"

def load_questions(path = QUESTIONS_FILE) :
    questions = json.loads(path.read_text(encoding="utf-8"))
    return questions

def pick_question(questions, topic=None) :
    if topic is not None:
        filtered_questions = [item for item in questions if item.get("topic") == topic]
        return random.choice(filtered_questions)
    return random.choice(questions)

def save_answer(question, answer, path=ANSWERS_FILE) :
    if path.exists() :
        answers = json.loads(path.read_text(encoding="utf-8"))
    else:
        answers = []
    answers.append({"question": question["question"], "answer": answer})
    path.write_text(json.dumps(answers, indent=2), encoding="utf-8")

def main() :
    topic = input("Enter preferred topic if any : ")
    if topic == "" :
        topic = None
    print("Chosen topic :", topic)
    questions = load_questions()
    picked_question = pick_question(questions, topic)
    print("Picked Question :", picked_question["question"])
    answer = input("Enter your answer : ")
    save_answer(picked_question, answer)
    print("Operation successful")

if __name__ == "__main__" :
    main()