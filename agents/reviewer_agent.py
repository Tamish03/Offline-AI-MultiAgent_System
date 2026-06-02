from agents.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Reviewer Agent",
            role="Quality Reviewer",
            system_prompt="""
You are an expert technical editor.

Your job is to review the provided draft document and return a polished, finalized, and significantly improved version of the document.

Rules:
- Address any issues with accuracy, clarity, structure, and completeness.
- Output ONLY the final polished markdown document itself.
- Do NOT include any meta-commentary, strengths, weaknesses, explanations, or section labels (like "Revised Version:").
- Only return the improved content.
"""
        )

    def review(
        self,
        content
    ):

        result = self.think(
            f"Review this document:\n\n{content}"
        )

        

        return result