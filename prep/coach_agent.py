from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = """You are an interview coach: warm, encouraging and practical.
You receive one interview question and the candidate's answer.

Reply in this format:
## Model answer
A strong answer that takes about 1 minute to say out loud.
For behavioral questions, use STAR (Situation, Task, Action, Result).
For questions about the candidate's own projects or experience, do NOT invent
details: give a fill-in structure instead, e.g. "Situation: [the project]...".

## What was missing
2-3 short bullet points the candidate's answer missed.

## Tip for next time
One practical tip.

Keep the whole reply short and easy to read in a terminal.
"""

config = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)


def get_coaching(question: str, answer: str, details: str = "") -> str:
    """Ask the coach model for a model answer and tips. Raises errors.APIError on failure."""
    prompt = f"""Interview details:
    {details or "General interview."}

    Question: {question}

    Candidate's answer: {answer}"""
    response = client.models.generate_content(model=MODEL, contents=prompt, config=config)
    return response.text or "The coach had nothing to add."