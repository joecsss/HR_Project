"""Resume parser service — extracts data from PDF/DOCX and de-identifies."""

import json
import os
from typing import Optional
from openai import OpenAI
from app.config import get_settings

settings = get_settings()


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    import pdfplumber

    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from a DOCX file."""
    from docx import Document

    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(file_path: str) -> str:
    """Extract text from a resume file (PDF or DOCX)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def parse_resume_with_llm(text: str) -> dict:
    """Use LLM to extract structured data from resume text."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""Analyze the following resume text and extract structured information.
Return a JSON object with these fields:
- "name": full name of the candidate
- "email": email address
- "phone": phone number
- "skills": list of technical and soft skills
- "experience": list of work experiences, each with "company", "title", "duration", "description"
- "education": list of education entries, each with "institution", "degree", "field", "year"
- "languages": list of languages spoken
- "summary": brief professional summary (2-3 sentences)
- "experience_years": estimated total years of experience (number)

If a field is not found, use null for strings/numbers or empty list for arrays.

Resume text:
{text[:6000]}

Return ONLY valid JSON, no other text."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result


def de_identify(parsed_data: dict) -> dict:
    """Remove PII from parsed resume data to prevent bias."""
    de_identified = parsed_data.copy()
    # Remove personally identifiable information
    de_identified["name"] = "[REDACTED]"
    de_identified["email"] = "[REDACTED]"
    de_identified["phone"] = "[REDACTED]"
    return de_identified


def create_embedding_text(de_identified_data: dict) -> str:
    """Create a text representation from de-identified data for embedding."""
    parts = []

    if de_identified_data.get("summary"):
        parts.append(f"Summary: {de_identified_data['summary']}")

    skills = de_identified_data.get("skills", [])
    if skills:
        parts.append(f"Skills: {', '.join(skills) if isinstance(skills, list) else skills}")

    for exp in de_identified_data.get("experience", []):
        if isinstance(exp, dict):
            parts.append(
                f"Experience: {exp.get('title', '')} at {exp.get('company', '')} - {exp.get('description', '')}"
            )

    for edu in de_identified_data.get("education", []):
        if isinstance(edu, dict):
            parts.append(
                f"Education: {edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}"
            )

    return "\n".join(parts)


def process_resume(file_path: str) -> dict:
    """Full pipeline: extract text → parse with LLM → de-identify → prepare for embedding."""
    raw_text = extract_text(file_path)
    parsed_data = parse_resume_with_llm(raw_text)
    de_identified_data = de_identify(parsed_data)
    embedding_text = create_embedding_text(de_identified_data)

    return {
        "parsed_data": parsed_data,
        "de_identified_data": de_identified_data,
        "embedding_text": embedding_text,
        "raw_text_length": len(raw_text),
    }
