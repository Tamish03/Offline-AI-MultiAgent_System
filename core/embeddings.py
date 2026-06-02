import requests
import numpy as np

from config import OLLAMA_URL, EMBEDDING_MODEL


def get_embedding(text):
    """
    Get embedding vector from Ollama
    using nomic-embed-text.

    Returns numpy array or None on failure.
    """

    text = text[:2000].strip()

    if not text:
        return None

    try:

        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        embedding = data.get(
            "embedding",
            []
        )

        if embedding:

            return np.array(
                embedding,
                dtype=np.float32
            )

    except Exception:

        pass

    return None
