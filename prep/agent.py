import prep.interview as interview
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv

load_dotenv()
questions = interview.load_questions()
client = genai.Client()

def get_topics() -> list[str]:
    """Return the list of interview topics available in the question bank.

    Use this to see which topics exist before asking for a question on a
    specific topic.
    """
    topics = interview.list_topics(questions)
    return sorted(topics)

def get_question(topic: str | None=None) -> dict:
    """Return one random interview question, optionally from a single topic.

    Args:
        topic: Topic to pick from. Must be one of the values returned by
            get_topics(). Leave it out to get a question from any topic.

    Returns:
        A dict with "topic" and "question". If the topic is unknown, returns
        a dict with "error" and "available_topics" instead.
    """
    topics = get_topics()
    if topic is not None and topic not in topics:
        return {"error": "topic not found", "available_topics": topics}
    question = interview.pick_question(questions, topic)
    return question

def main():
    config = types.GenerateContentConfig(
        tools=[get_topics, get_question],    # your two wrapper functions (no brackets!)
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Give me one interview question about python",
        config=config,
    )
    print("Text:", response.text)
    for call in response.function_calls or []:
        print("AI wants to run:", call.name, call.args)

if __name__ == "__main__" :
    main()