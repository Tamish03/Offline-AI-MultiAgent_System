from agents.base_agent import BaseAgent


class ResponseAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Response Agent",
            role="General Assistant",
            system_prompt="""
You are a helpful AI assistant.

Rules:

- Answer directly.
- Be concise.
- If code is requested, provide complete code.
- If explanation is requested, explain clearly.
- If a greeting is given, respond naturally.
- Do not create reports unless asked.
- Do not create articles unless asked.
- Do not overcomplicate simple questions.
- Keep responses practical and useful.
"""
        )

    def respond(
        self,
        prompt,
        history=None
    ):

        return self.think(
            prompt,
            history=history
        )

    def respond_stream(
        self,
        prompt,
        history=None
    ):
        """Stream response tokens in real-time."""

        yield from self.think_stream(
            prompt,
            history=history
        )