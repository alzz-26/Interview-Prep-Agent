# Interview Prep Agent: an agentic AI learning project

A terminal-based mock interviewer built with three cooperating AI agents.
Give it a job description and your resume, and it runs a tailored interview,
scores your answers, asks follow-ups, coaches you on weak answers, and remembers
your weak topics across sessions.

As a final-year student, online assessments and interviews are a big part of my
year, so I wanted a practice partner that adapts to each job I apply for.
After contributing to [Project NANDA](https://github.com/projnanda/nandatown/pull/303),
an open-source project for AI agents, I decided to learn agentic AI properly by
building this, and to brush up my Python along the way.

## What it does
- **Parser agent**: turns a job description (PDF/TXT/MD) and an optional resume into an interview brief
- **Interviewer agent**: asks bank or self-written questions, scores answers, asks one
  follow-up based on the score (gap or stretch question), gives feedback
- **Coach agent**: on request, writes a model answer (STAR for behavioral) and tips,
  saved to `coach_notes.md` for revision
- **Memory**: scores and answer times per topic; the interviewer starts with your weakest topic
- **Archive**: a new interview brief archives the previous interview's files per company

## Agentic AI concepts covered
| Concept | Where |
|---|---|
| LLM API calls, system instructions | `prep/feedback.py` |
| Tool / function calling | `prep/agent.py` (`get_question`, `record_answer`, ...) |
| The agent loop (manual, with step limit) | `run_agent()` in `prep/agent.py` |
| Short-term memory (conversation log) | `contents` list in `prep/agent.py` |
| Long-term memory (stats injected into the prompt) | `topic_stats()` + `past_performance_summary()` |
| Multi-agent: pipeline | parser agent → `interview_details.txt` → interviewer |
| Multi-agent: agent as a tool | interviewer calls the coach via `ask_coach` |
| Error handling for rate limits (retry 429/5xx only) | `main()` in `prep/agent.py` |

## Setup
Requires Python 3.11+ and a [Gemini API key](https://aistudio.google.com/) (the free tier works).

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; on macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your-key-here
```

## Usage
```bash
python -m prep.parser_agent   # build an interview brief from a JD (+ resume)
python -m prep.agent          # start the mock interview (type "quit" to stop)
python -m pytest              # run the tests
```
No JD yet? Copy `prep/interview_details.example.txt` to `prep/interview_details.txt`
and fill it in by hand.

Note: the free tier allows only a few requests per minute; one answer can take
2–3 requests, so the agent waits and retries when it hits the limit.

## How I learned: the `learn-by-building` skill
I wrote all the code myself, with Claude as a **tutor, not a code generator**:
concepts first, then hints, a fill-in-the-blanks skeleton only if stuck, and
reviews of my code by reading. I packaged this method as a reusable
[Claude Code skill](.claude/skills/learn-by-building/SKILL.md). Copy that folder into
any project and run `/learn-by-building <your idea>`.

## Privacy
Personal files (`.env`, interview details, answers, coach notes, archive) are git-ignored.
On the Gemini free tier, prompts may be used by Google to improve its products,
so don't put contact details or sensitive data in your resume or brief.

## Next
- A web UI (FastAPI backend + HTML/CSS/JS frontend)