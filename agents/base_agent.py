from core.ollama_client import chat, chat_stream
from config import DEFAULT_MODEL


class BaseAgent:

    def __init__(
        self,
        name,
        role,
        system_prompt,
        model=DEFAULT_MODEL
    ):

        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model

    def think(
        self,
        prompt,
        history=None
    ):

        response = chat(
            prompt=prompt,
            model=self.model,
            system=self.system_prompt,
            history=history or []
        )

        return response

    def think_stream(
        self,
        prompt,
        history=None
    ):
        """Stream response tokens in real-time."""

        yield from chat_stream(
            prompt=prompt,
            model=self.model,
            system=self.system_prompt,
            history=history or []
        )

    def clear_history(self):

        pass

    def __str__(self):

        return f"{self.name} ({self.model})"