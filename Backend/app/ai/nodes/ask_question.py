from __future__ import annotations

from app.ai.prompts import PROMPT_QUESTION, SYSTEM_QUESTION
from app.ai.services.gemini import GeminiService
from app.ai.state import TeacherAction, TeacherState


async def ask_question_node(state: TeacherState) -> dict:
    gemini = GeminiService()

    prompt = PROMPT_QUESTION.format(
        teaching_content=state.get("teaching_content", ""),
    )

    question = await gemini.generate(prompt, SYSTEM_QUESTION)

    history = list(state.get("conversation_history", []))
    history.append({"role": "teacher", "content": f"Question: {question}"})

    return {
        "question": question,
        "current_action": TeacherAction.EVALUATE_RESPONSE,
        "conversation_history": history,
    }
