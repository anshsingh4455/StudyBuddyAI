"""
prompts/templates.py

Prompt templates for different StudyBuddy AI tasks:
- Text tutor (explain, examples, practice questions, quiz, study plan)
- Image doubt solver (question/problem vs. explanation)
- Explain-only mode for notes (text and image)

These functions create detailed, student-friendly prompts that guide the LLM
to produce clear, structured responses.
"""

from typing import List, Dict


def _format_chat_history(chat_history: List[Dict[str, str]]) -> str:
    """Format the last few messages from chat history for additional context."""
    if not chat_history:
        return ""

    recent = chat_history[-3:]
    lines = []
    for msg in recent:
        user = msg.get("user", "")
        assistant = msg.get("assistant", "")
        if user:
            lines.append(f"Student: {user}")
        if assistant:
            lines.append(f"Tutor: {assistant}")
    return "\n".join(lines)


def build_text_tutor_prompt(
    user_input: str,
    student_level: str,
    task_type: str,
    chat_history: List[Dict[str, str]] | None = None,
) -> str:
    """Build a prompt for the text chat tutor."""
    level = (student_level or "Beginner").strip()
    task = (task_type or "Explain").strip()

    base_instructions = f"""
You are **StudyBuddy AI**, a friendly and patient tutor helping a {level.lower()} student.

Student level: {level}
Requested task type: {task}
"""

    task_instructions = {
        "Explain": (
            "Explain the topic step by step in simple language. "
            "Use short sentences, everyday examples, and clear headings."
        ),
        "Examples": (
            "Provide several practical examples that illustrate the main ideas. "
            "Start with very easy examples, then slightly harder ones."
        ),
        "Practice Questions": (
            "Create 3–7 practice questions with answers and brief explanations. "
            "Include a mix of easy and moderate questions."
        ),
        "Quiz": (
            "Create a short quiz of 5 questions. "
            "Show the correct answers and short explanations at the end."
        ),
        "Study Plan": (
            "Create a clear, structured study plan with daily or weekly steps, "
            "estimated time, and learning goals for each step."
        ),
    }

    task_text = task_instructions.get(task, task_instructions["Explain"])

    history_text = _format_chat_history(chat_history or [])
    history_block = f"Previous conversation:\n{history_text}\n\n" if history_text else ""

    return (
        f"{base_instructions}\n"
        f"{history_block}"
        f"Your job:\n"
        f"{task_text}\n\n"
        f"Student's question or topic:\n"
        f"{user_input}\n\n"
        "Please respond in Markdown with:\n"
        "- Clear headings (### ...)\n"
        "- Bullet points for lists\n"
        "- Step-by-step explanations where helpful\n"
        "- A short recap section at the end titled 'Summary'\n"
    )


def build_image_solver_prompt(ocr_text: str, is_question: bool) -> str:
    """Build a prompt for the image doubt solver based on extracted text."""
    mode_text = (
        "The text below is a question or problem that the student wants you to solve."
        if is_question
        else "The text below contains notes or textbook-style explanations that the student wants you to explain."
    )

    task_text = (
        "1. Briefly restate what the question is asking.\n"
        "2. Solve it step by step, showing your reasoning.\n"
        "3. Explain each step in simple, beginner-friendly language.\n"
        "4. If there are formulas, name and explain them.\n"
        "5. Finish with a short recap of the main idea."
        if is_question
        else "1. Identify the main ideas and key concepts.\n"
        "2. Explain each part in simple, clear language.\n"
        "3. Use headings and bullet points to organize the explanation.\n"
        "4. Add a short recap of the big picture at the end."
    )

    return (
        "You are **StudyBuddy AI**, a friendly tutor.\n\n"
        f"{mode_text}\n\n"
        "Here is the text extracted from the student's image:\n"
        "-----\n"
        f"{ocr_text}\n"
        "-----\n\n"
        "Your tasks:\n"
        f"{task_text}\n\n"
        "Respond in Markdown with clear headings and bullet points."
    )


def build_explain_notes_text_prompt(notes_text: str) -> str:
    """
    Build a prompt to explain notes (text input) with a strict 'no extra info' rule.
    """
    return (
        "You are **StudyBuddy AI**, a careful tutor.\n\n"
        "The student has pasted their own notes. Your job is ONLY to explain and clarify\n"
        "what is already written in the notes. **Do not add any new facts, formulas, or examples**\n"
        "that are not clearly present in the notes, unless the student later asks for more.\n\n"
        "Here are the student's notes:\n"
        "-----\n"
        f"{notes_text}\n"
        "-----\n\n"
        "Please:\n"
        "- Explain each part in simple, clear language.\n"
        "- Clarify any confusing or technical words using only the information present.\n"
        "- Organize the explanation with headings and bullet points.\n"
        "- End with a short 'Summary of Your Notes' section.\n"
    )


def build_explain_notes_image_prompt(ocr_text: str) -> str:
    """
    Build a prompt to explain notes (image input) with a strict 'no extra info' rule.
    """
    return (
        "You are **StudyBuddy AI**, a careful tutor.\n\n"
        "The student took a photo of their notes or textbook. The text below is the\n"
        "content we could read from that image. Your job is ONLY to explain and clarify\n"
        "what is already written there. **Do not add new facts, formulas, or examples**\n"
        "that are not clearly present in the text below.\n\n"
        "Extracted text from the student's image:\n"
        "-----\n"
        f"{ocr_text}\n"
        "-----\n\n"
        "Please:\n"
        "- Explain the content in simple words.\n"
        "- Clarify tricky or technical parts using only this text.\n"
        "- Use headings and bullet points.\n"
        "- End with a short 'Summary of What Your Notes Say' section.\n"
    )

