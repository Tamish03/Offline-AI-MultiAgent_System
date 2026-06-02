from agents.base_agent import BaseAgent


class WriterAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Writer Agent",
            role="Content Writer",
            system_prompt="""
You are an expert technical writer and educator.

Your responsibilities:

- Explain concepts clearly
- Provide syntax when relevant
- Provide code examples when relevant
- Provide practical examples
- Provide best practices
- Use headings and bullet points
- Avoid repetition

Rules:

1. If topic is technical:
   - Include syntax
   - Include example

2. If topic involves coding:
   - Include complete code
   - Include explanation

3. If topic is conceptual:
   - Include explanation
   - Include key concepts
   - Include practical applications

4. Keep answers concise.

5. Maximum 600 words.

6. Never repeat sections.

7. Return one final answer only.
"""
        )

    def write(
        self,
        topic,
        research=None
    ):

        research_summary = ""

        if research:

            research_summary = research

        prompt = f"""
Topic:

{topic}

Research Summary:

{research_summary}

Create a final polished response.

Requirements:

- Use markdown headings
- Include explanation
- Include syntax if applicable
- Include code example if applicable
- Include practical example if applicable
- Include best practices if applicable
- Maximum 600 words
- Do not repeat content
"""

        result = self.think(
            prompt
        )

        return result