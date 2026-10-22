import time
import prep.interview as interview
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
client = genai.Client()
MAX_STEPS = 5
JD_FILE = Path(__file__).parent/"interview_details.txt"
JD = JD_FILE.read_text(encoding="utf-8") if JD_FILE.exists() else "General software / AI interview"

def get_topics() -> list[str]:
    """Return the list of interview topics available in the question bank.

    Use this to see which topics exist before asking for a question on a
    specific topic.
    """
    questions = interview.load_questions()
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
    questions = interview.load_questions()
    topics = get_topics()
    if topic is not None and topic not in topics:
        return {"error": "topic not found", "available_topics": topics}
    question = interview.pick_question(questions, topic)
    return question

def save_question(topic: str, question: str) -> dict:
    """Saves the generated question in the question bank. Called after a new question is generated.
    
    Args:
        topic: The topic of the question.
        question: The question asked.
    
    Returns:
        A dict to support JSON format simply stating the success/saved status.
    """
    interview.add_question(topic, question)
    return {"saved": True}

def record_answer(topic: str, question: str, answer: str, score: int) -> dict:
    """Saves the question, topic, answer and the score obtained 
    in a file. Called just after the user gives the answer as input.
    
    Args:
        topic: The topic of the given question.
        question: The given question.
        answer: The answer taken from user input.
        score: The score obtained on the answer out of 10.
    
    Returns:
        A dict to support JSON format simply stating the success/saved status.
    """
    question = {"topic": topic, "question": question}
    interview.save_answer(question, answer, score)
    return {"saved": True}

MODEL = "gemini-3.6-flash"
TOOL_FUNCTIONS = [get_topics, get_question, record_answer, save_question]
TOOLS = {f.__name__: f for f in TOOL_FUNCTIONS}

def past_performance_summary() -> str:
    """Summarise past scores per topic, weakest first, for the system instruction."""
    stats = interview.topic_stats(interview.load_answers())
    if not stats:
        return "No previous sessions."
    weakest_first = sorted(stats.items(), key=lambda item: item[1]["avg_score"])
    lines = [
        f"- {topic}: average {s['avg_score']}/10 over {s['count']} answers"
        for topic, s in weakest_first
    ]
    return "\n".join(lines)

PAST_PERFORMANCE = past_performance_summary()

SYSTEM_INSTRUCTION = f"""You are a mock interviewer: kind and encouraging, but you evaluate fairly and strictly.

# Interview details
{JD}

# Candidate's past performance (weakest first)
{PAST_PERFORMANCE}

# How to run the interview
1. Greet the candidate briefly and ask which topic they want to start with.
   Offer the topics from the Focus topics above.
2. Ask ONE question at a time. Either:
   - get one from the bank with get_question and ask it word for word, or
   - write your own question tailored to the interview details, then save it
     with save_question using a topic label from the Focus topics.
3. Wait for the candidate's answer. Never answer a question yourself.
4. Score the answer out of 10 (privately, for now).
5. Call record_answer right away with the topic, exact question, answer and score.
6. Decide on a follow-up based on the score:
   - Score below 6: ask ONE follow-up about the biggest gap in the answer,
     to give the candidate a chance to improve it.
   - Score 6 to 8: no follow-up, go straight to feedback (step 9).
   - Score above 8: ask ONE harder "stretch" follow-up that goes deeper
     into the same topic (e.g. edge cases, trade-offs, real-world use).
   Never ask more than one follow-up per question.
7. If you asked a follow-up, wait for the candidate's answer and then score it 
   again out of 10 privately.
8. Call record_answer again for it, with the same topic, the follow-up
   question text only without any greeting or comments as the question,
   its answer and its own score.
9. Give brief feedback: the score out of 10, one strength, one improvement.
   If there was a follow-up, mention how the follow-up answer changed the score.
10. Ask whether they want another question, and on which topic.

# Rules
- Keep your messages short; this is a conversation, not an essay.
- Use the tools only when needed; do not call get_topics if the topics are
  already listed above.
- Prioritise topics with an average below 6. When greeting, briefly mention
  the weakest topic and suggest starting there, but let the candidate choose.
"""
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
    """Runs the AI agent for mock interview."""
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
            if user_text.lower() == ("quit" or "exit"):
                print("Thanks for the motivation to prepare. Good luck! Ending...")
                break
            contents.append(types.Content(role="user", parts=[types.Part(text=user_text)]))
    except KeyboardInterrupt:
        print("User interrupted the conversation. Ending...")

if __name__ == "__main__" :
    main()