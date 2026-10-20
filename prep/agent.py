import time

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

def record_answer(topic: str, question: str, answer: str) -> dict:
    """Saves the question, topic and answer in a file. Called just after the user gives the answer as input.
    
    Args:
        topic: The topic of the given question.
        question: The given question.
        answer: The answer taken from user input.
    
    Returns:
        A dict to support JSON format simply stating the success/saved status.
    """
    question = {"topic": topic, "question": question}
    interview.save_answer(question, answer)
    return {"saved": True}

MODEL = "gemini-3.6-flash"
MAX_STEPS = 5
TOOL_FUNCTIONS = [get_topics, get_question, record_answer]
TOOLS = {f.__name__: f for f in TOOL_FUNCTIONS}
SYSTEM_INSTRUCTION = "Imagine yourself as an mock interviewer who is kind and soft but evaluates fairly and strictly. The following are the steps you are required to follow:\n" \
"1. Greet, and ask which topic the user wants to practise.\n" \
"2. Get a question with the tool and ask it word for word, one at a time.\n" \
"3. Wait for the answer, then call record_answer.\n" \
"4. Give brief feedback: a score out of 10, one strength, one improvement.\n" \
"5. Ask whether they want another question."

config = types.GenerateContentConfig(
    tools=TOOL_FUNCTIONS,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    system_instruction=SYSTEM_INSTRUCTION,
)

def run_agent(content: list) -> str:
    """Run the tool loop until the AI gives a final text answer."""
    for step in range(MAX_STEPS):
        response = client.models.generate_content(model=MODEL, contents=content, config=config)
        if not response.function_calls:
            content.append(response.candidates[0].content)
            return response.text
        content.append(response.candidates[0].content)
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
        content.append(types.Content(role="user", parts=result_parts))

    return "Stopped: too many steps."

def main():
    contents = [types.Content(role="user", parts=[types.Part(text="Start the interview.")])]
    try:
        while True:
            try:
                print(run_agent(contents))
            except errors.APIError as e:
                if e.code==429 or e.code>=500:
                    print(f"API busy ({e.code}). Retrying in 60 seconds...")
                    time.sleep(60)
                    continue 
                print("API error occurred:", e.message)
                break
            user_text = input("You: ").strip()
            while not user_text:
                user_text = input("You: ").strip()
            contents.append(types.Content(role="user", parts=[types.Part(text=user_text)]))
    except KeyboardInterrupt:
        print("User interrupted the conversation. Ending...")

if __name__ == "__main__" :
    main()