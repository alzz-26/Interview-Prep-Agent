from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
import prep.interview as interview
import json

load_dotenv()
MODEL = "gemini-3.8-flash"
SYSTEM_INSTRUCTION = "Imagine yourself as an interviewer who is kind and soft but evaluates fairly and strictly. Given the question and the answer, evaluate and give a score out of 10. Provide a consice description of what you liked/disliked."
client = genai.Client()

def get_feedback(question: str, answer: str) -> str:
    """Ask Gemini to score an interview answer and return the feedback text."""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"Question: {question}\nAnswer: {answer}",
            config= types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.2),
        )
        return response.text if response.text is not None else "Sorry, could not generate a response."
    except errors.APIError as e:
        return f"No response generated - {e.message}"

def main():
    """Runs the full interview pipeline with added AI based feedback from GEMINI API."""
    interview.main()
    answers = json.loads(interview.ANSWERS_FILE.read_text(encoding="utf-8"))
    question = answers[-1]["question"]
    answer = answers[-1]["answer"]
    print("Question: ", question)
    print("Answer: ", answer)
    print("Feedback: ", get_feedback(question, answer))

if __name__ == "__main__" :
    main()