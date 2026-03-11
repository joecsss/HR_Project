"""JD Authoring service — AI-powered Job Description generation."""

import json
from openai import OpenAI
from app.config import get_settings
from typing import Optional

settings = get_settings()


def generate_job_description(
    title: str,
    department: Optional[str] = None,
    seniority_level: Optional[str] = None,
    key_skills: Optional[str] = None,
    additional_notes: Optional[str] = None,
) -> dict:
    """Generate a full job description using LLM."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    context_parts = [f"Job Title: {title}"]
    if department:
        context_parts.append(f"Department: {department}")
    if seniority_level:
        context_parts.append(f"Seniority Level: {seniority_level}")
    if key_skills:
        context_parts.append(f"Key Skills Required: {key_skills}")
    if additional_notes:
        context_parts.append(f"Additional Notes: {additional_notes}")

    context = "\n".join(context_parts)

    prompt = f"""You are an HR professional. Generate a comprehensive job description based on the following information:

{context}

Return a JSON object with exactly these fields:
- "description": A detailed job description (3-5 paragraphs) covering the role overview, responsibilities, and what success looks like
- "requirements": Bullet-pointed requirements listing qualifications, skills, and experience needed (use \\n for line breaks)
- "benefits": Bullet-pointed list of what the company offers (use \\n for line breaks)

Make the description professional, engaging, and inclusive. Avoid gendered language.
Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result


def create_jd_embedding_text(job_data: dict) -> str:
    """Create text representation of a job for embedding."""
    parts = []
    if job_data.get("title"):
        parts.append(f"Title: {job_data['title']}")
    if job_data.get("department"):
        parts.append(f"Department: {job_data['department']}")
    if job_data.get("description"):
        parts.append(f"Description: {job_data['description']}")
    if job_data.get("requirements"):
        parts.append(f"Requirements: {job_data['requirements']}")
    return "\n".join(parts)
