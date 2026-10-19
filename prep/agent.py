import prep.interview as interview
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv

load_dotenv()
questions = interview.load_questions()
client = genai.Client()
MAX_STEPS = 5

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

MODEL = "gemini-3.6-flash"
MAX_STEPS = 5
TOOL_FUNCTIONS = [get_topics, get_question]
TOOLS = {f.__name__: f for f in TOOL_FUNCTIONS}

config = types.GenerateContentConfig(
    tools=TOOL_FUNCTIONS,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

def run_agent(user_message: str) -> str:
    """Run the tool loop until the AI gives a final text answer."""
    contents = [types.Content(role="user", parts=[types.Part(text=user_message)])]

    for step in range(MAX_STEPS):
        response = client.models.generate_content(model=MODEL, contents=contents, config=config)
        if not response.function_calls:
            return response.text
        contents.append(response.candidates[0].content)
        result_parts = []
        for call in response.function_calls:
            print("🔧", call.name, call.args)
            tool = TOOLS.get(call.name)
            if tool is None:
                result = {"error": "Tool not found", "available_tools": list(TOOLS.keys())}
            else:
                result = tool(**call.args)
            result_parts.append(
                types.Part.from_function_response(name=call.name, response={"result": result})
            )
        contents.append(types.Content(role="user", parts=result_parts))

    return "Stopped: too many steps."

def main():
    print(run_agent("Give me one interview question about nanda"))

if __name__ == "__main__" :
    main()