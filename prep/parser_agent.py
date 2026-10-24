from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
client = genai.Client()
TEMPLATE_FILE = Path(__file__).parent/"interview_details.example.txt"
template = TEMPLATE_FILE.read_text(encoding="utf-8")
MODEL = "gemini-3.6-flash"
SYSTEM_INSTRUCTION = f"""You turn a job description and an optional resume into an interview brief.

# Template (fill in this exact format)
{template}

# Rules
1. Fill in only from the documents. Write [unknown] instead of guessing.
2. Leave out the "How to use this file" section.
3. Topic labels: short and lowercase (e.g. agents, testing, behavioral).
4. Output only the filled template, with no extra comments.
"""

def read_document(path: str | Path) -> types.Part:
    """Read a document about the job description or the resume.
    PDFs become bytes and .txt/.md files become text Return it
    as a Part object.
    Supported file types: pdf, txt, md"""
    path = Path(path)
    extension = path.suffix.lower()
    file_in_bytes = path.read_bytes()
    if extension == ".pdf":
        return types.Part.from_bytes(
            data=path.read_bytes(),
            mime_type="application/pdf"
        )
    elif extension == ".md" or extension == ".txt":
        mime = "text/markdown"
        return types.Part(
            text=path.read_text(encoding="utf-8")
        )
    else:
        raise ValueError(f"Unsupported file type: {extension} (use pdf, txt or md)")

def build_interview_details(jd_path: Path, resume_path: Path | None = None) -> str:
    """Build the complete interview details by reading the job description
    and resume"""
    jd_part = read_document(jd_path)
    resume_part = read_document(resume_path)
    contents = [types.Part(text="Job description:"), jd_part]
    if resume_path is not None:
        contents += [types.Part(text="Candidate's resume:"), read_document(resume_path)]
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config= types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )
    return response.text if response.text is not None else "Sorry, could not generate a response."

DETAILS_FILE = Path(__file__).parent / "interview_details.txt"

def ask_path(prompt: str) -> Path | None:
    """Ask for a file path; return None if left empty."""
    text = input(prompt).strip().strip('"')    # Windows "Copy as path" adds quotes
    return Path(text) if text else None

def main():
    """Turn a job description (and optional resume) into interview_details.txt."""
    jd_path = ask_path("Job description file (pdf/txt/md): ")
    if jd_path is None or not jd_path.exists():
        print("Job description file not found. Ending.")
        return

    resume_path = ask_path("Resume file (optional, press Enter to skip): ")
    if resume_path is not None and not resume_path.exists():
        print("Resume not found, continuing without it.")
        resume_path = None

    try:
        details = build_interview_details(jd_path, resume_path)
    except (ValueError, errors.APIError) as e:
        print("Could not build interview details:", e)
        return

    print("\n" + details + "\n")
    choice = input(f"Save to {DETAILS_FILE.name}? This overwrites the current file (y/n): ")
    if choice.strip().lower() == "y":
        DETAILS_FILE.write_text(details, encoding="utf-8")
        print("Saved. Run `python -m prep.agent` to practise with it.")
    else:
        print("Not saved.")

if __name__ == "__main__":
    main()