"""Embedding generation service using OpenAI."""

from openai import OpenAI
from app.config import get_settings
from typing import List, Optional
import numpy as np

settings = get_settings()

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def generate_embedding(text: str) -> List[float]:
    """Generate an embedding vector for the given text using OpenAI."""
    if not text or not text.strip():
        return [0.0] * 1536

    client = _get_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000],  # Limit input length
    )
    return response.data[0].embedding


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
