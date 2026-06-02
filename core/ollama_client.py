import requests
import json

OLLAMA_URL = "http://localhost:11434"


def chat(
    prompt,
    model="qwen2.5:1.5b",
    system=None,
    history=None,
    temperature=0.7
):
    messages = []

    if system:
        messages.append({
            "role": "system",
            "content": system
        })

    if history:
        messages.extend(history)

    messages.append({
        "role": "user",
        "content": prompt
    })

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def chat_stream(
    prompt,
    model="qwen2.5:1.5b",
    system=None,
    history=None,
    temperature=0.7
):
    """
    Stream tokens from Ollama as they generate.
    Yields each token as a string.
    """
    messages = []

    if system:
        messages.append({
            "role": "system",
            "content": system
        })

    if history:
        messages.extend(history)

    messages.append({
        "role": "user",
        "content": prompt
    })

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        },
        stream=True
    )

    response.raise_for_status()

    for line in response.iter_lines():

        if line:

            chunk = json.loads(line)

            token = (
                chunk
                .get("message", {})
                .get("content", "")
            )

            if token:
                yield token