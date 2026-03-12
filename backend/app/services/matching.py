"""Matching Engine — cosine similarity + LLM reranker for candidate-job matching."""

import json
from openai import OpenAI
from app.config import get_settings
from app.services.embedding import cosine_similarity
from typing import List, Optional

settings = get_settings()


def compute_match_score(candidate_embedding: List[float], job_embedding: List[float]) -> float:
    """Compute raw similarity score between candidate and job embeddings."""
    similarity = cosine_similarity(candidate_embedding, job_embedding)
    # Convert to 0-100 scale
    return round(max(0, min(100, similarity * 100)), 2)


def rerank_with_llm(
    candidate_data: dict,
    job_data: dict,
    initial_score: float,
) -> dict:
    """Use LLM to provide detailed match analysis and refined score."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Prepare candidate summary (de-identified)
    candidate_summary = []
    if candidate_data.get("skills"):
        skills = candidate_data["skills"]
        if isinstance(skills, list):
            skills = ", ".join(skills)
        candidate_summary.append(f"Skills: {skills}")
    if candidate_data.get("experience"):
        for exp in candidate_data.get("experience", []):
            if isinstance(exp, dict):
                candidate_summary.append(
                    f"Experience: {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
                )
    if candidate_data.get("education"):
        for edu in candidate_data.get("education", []):
            if isinstance(edu, dict):
                candidate_summary.append(
                    f"Education: {edu.get('degree', '')} in {edu.get('field', '')}"
                )

    prompt = f"""You are an expert HR recruiter. Analyze how well this candidate matches the job position.

Job Title: {job_data.get('title', 'N/A')}
Job Description: {job_data.get('description', 'N/A')[:2000]}
Job Requirements: {job_data.get('requirements', 'N/A')[:1000]}

Candidate Profile (de-identified):
{chr(10).join(candidate_summary)}

Initial similarity score: {initial_score}/100

Provide a detailed analysis. Return a JSON object with:
- "score": refined match score (0-100), considering both the initial score and your analysis
- "reasoning": 2-3 sentence summary of why this candidate matches or doesn't match
- "strengths": list of 3-5 specific strengths relative to this job
- "gaps": list of areas where the candidate may fall short
- "recommendation": one of "Strong Match", "Good Match", "Moderate Match", "Weak Match"

Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result


def match_candidate_to_job(
    candidate_embedding: List[float],
    job_embedding: List[float],
    candidate_data: dict,
    job_data: dict,
) -> dict:
    """Full matching pipeline: embedding similarity + LLM reranking."""
    # Step 1: Compute embedding similarity
    initial_score = compute_match_score(candidate_embedding, job_embedding)

    # Step 2: LLM reranking for detailed analysis
    match_result = rerank_with_llm(candidate_data, job_data, initial_score)

    return {
        "initial_score": initial_score,
        "final_score": match_result.get("score", initial_score),
        "reasoning": match_result.get("reasoning", ""),
        "strengths": match_result.get("strengths", []),
        "gaps": match_result.get("gaps", []),
        "recommendation": match_result.get("recommendation", ""),
    }


def compare_candidates_with_llm(
    candidates_data: List[dict],
    job_data: dict,
) -> dict:
    """Use LLM to compare multiple candidates against a job description."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    profiles_text = []
    for cand in candidates_data:
        profile = cand.get("profile", {})
        cand_id = cand.get("candidate_id", "Unknown")
        app_id = cand.get("application_id", "Unknown")
        name = cand.get("name", "Unknown")
        
        summary = [f"Candidate ID: {cand_id}", f"Application ID: {app_id}", f"Name: {name}"]
        if profile.get("skills"):
            skills = profile["skills"]
            if isinstance(skills, list):
                skills = ", ".join(skills)
            summary.append(f"Skills: {skills}")
        if profile.get("experience_years"):
            summary.append(f"Years of Experience: {profile.get('experience_years')}")
        if profile.get("education"):
             summary.append(f"Education: {profile.get('education')}")

        profiles_text.append("\n".join(summary))

    prompt = f"""You are an expert HR recruiter. Compare these candidates for the following job position.

Job Title: {job_data.get('title', 'N/A')}
Job Description: {job_data.get('description', 'N/A')[:2000]}
Job Requirements: {job_data.get('requirements', 'N/A')[:1000]}

Candidates:
{"\n---\n".join(profiles_text)}

Provide a detailed comparative analysis. Return a JSON object with:
- "candidates": A list of objects for each candidate containing:
    - "application_id": Match the application ID from the input
    - "candidate_id": Match the candidate ID from the input
    - "candidate_name": Name of the candidate
    - "strengths": List of 1-3 specific strengths for this job
    - "gaps": List of 1-3 specific gaps for this job
- "analysis": A 2-3 paragraph explanation of how the candidates compare to each other in relation to the job requirements.
- "recommended_application_id": The application ID of the candidate you recommend most (as an integer).

Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result

