from agents.base_agent import BaseAgent


class ContentAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Content Agent",
            role="Content Creator",
            system_prompt="""
You are an expert content creator.

Create:

- LinkedIn Posts
- Blog Posts
- Articles
- Emails
- Product Descriptions
- Social Media Content

Rules:

- Professional quality
- Engaging
- Platform specific
- No generic AI fluff
- Actionable
- Well structured

If LinkedIn:
- Hook
- Story or insight
- Takeaway
- CTA

Return only final content.
"""
        )

    def create_content(
        self,
        prompt,
        history=None
    ):

        return self.think(
            prompt,
            history=history
        )

    def create_content_stream(
        self,
        prompt,
        history=None
    ):
        """Stream content tokens in real-time."""

        yield from self.think_stream(
            prompt,
            history=history
        )