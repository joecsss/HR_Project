"""HR Chatbot service using LangChain for conversational AI assistant."""

from openai import OpenAI
from app.config import get_settings
from typing import List, Dict, Optional
import re

settings = get_settings()

# In-memory conversation store (use Redis in production)
_conversations: Dict[str, List[dict]] = {}

SYSTEM_PROMPT = """You are an AI HR Assistant for a recruitment platform. You help HR professionals with:

1. **Job Description Creation**: Help write or improve job descriptions when asked.
2. **Candidate Summarization**: Summarize candidate profiles and their qualifications.
3. **HR FAQ**: Answer common HR questions about recruitment best practices, compliance, and processes.
4. **General HR Support**: Provide guidance on hiring workflows, interview techniques, and onboarding.

Guidelines:
- Be professional, helpful, and concise
- Use inclusive language
- If you don't know something specific to the company, say so
- When creating JDs, ask clarifying questions if needed
- Support both Thai and English languages based on user input
- IMPORTANT: Only answer HR/recruitment-related questions.
- If the user asks off-topic questions (math homework, coding, entertainment, etc.),
  politely refuse and redirect to HR topics.

You do NOT have access to the actual database. If the user asks about specific candidates or jobs,
guide them to use the platform's dashboard features instead."""

OFF_TOPIC_MESSAGE = (
    "ขออภัย ฉันช่วยได้เฉพาะเรื่องงาน HR และการสรรหาเท่านั้น "
    "เช่น การเขียน JD, คัดกรองเรซูเม่, สรุปผู้สมัคร, วางคำถามสัมภาษณ์, และกระบวนการสรรหา"
)

HR_KEYWORDS = {
    "hr", "human resource", "human resources", "recruit", "recruitment", "hiring",
    "job", "job description", "jd", "interview", "candidate", "resume", "cv",
    "talent", "onboarding", "payroll", "benefit", "compliance", "workforce",
    "สรรหา", "รับสมัคร", "สมัครงาน", "ตำแหน่งงาน", "ประกาศงาน", "คำบรรยายงาน", "job description",
    "ผู้สมัคร", "เรซูเม่", "สัมภาษณ์", "คัดกรอง", "บุคคล", "บุคคลากร", "ทรัพยากรบุคคล",
    "พนักงาน", "เงินเดือน", "สวัสดิการ", "ทดลองงาน", "ประเมิน", "onboarding", "hr"
}


def _is_hr_related(message: str, context: Optional[str] = None) -> bool:
    text = f"{message} {context or ''}".lower()
    text = re.sub(r"\s+", " ", text)
    return any(keyword in text for keyword in HR_KEYWORDS)


def chat(
    message: str,
    session_id: str,
    context: Optional[str] = None,
) -> str:
    """Process a chat message and return AI response."""
    if not _is_hr_related(message=message, context=context):
        return OFF_TOPIC_MESSAGE

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Initialize conversation if new session
    if session_id not in _conversations:
        _conversations[session_id] = []

    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add context if provided
    if context:
        messages.append({
            "role": "system",
            "content": f"Additional context from the platform:\n{context}"
        })

    # Add conversation history (last 10 turns to stay within limits)
    messages.extend(_conversations[session_id][-20:])

    # Add current user message
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        max_tokens=1000,
    )

    assistant_message = response.choices[0].message.content

    # Store conversation history
    _conversations[session_id].append({"role": "user", "content": message})
    _conversations[session_id].append({"role": "assistant", "content": assistant_message})

    # Limit stored history
    if len(_conversations[session_id]) > 40:
        _conversations[session_id] = _conversations[session_id][-20:]

    return assistant_message


def clear_session(session_id: str):
    """Clear conversation history for a session."""
    if session_id in _conversations:
        del _conversations[session_id]
