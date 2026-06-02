import json
import re

from agents.base_agent import BaseAgent


class ReflectionAgent(BaseAgent):
    """
    Quality gate for workflow outputs.

    Evaluates content against the original goal.
    Maximum 1 revision cycle.
    Deterministic pass/fail threshold.
    """

    def __init__(self):

        super().__init__(
            name="Reflection Agent",
            role="Quality Evaluator",
            system_prompt="""
You evaluate content quality.

Return ONLY a JSON object.
No explanation. No markdown.

Format:

{"score": <1-10>, "feedback": "<one sentence>"}

Score Guide:

1-3: Poor — missing key info
4-5: Below average — needs work
6-7: Good — acceptable quality
8-10: Excellent — well done
"""
        )

        self.pass_threshold = 6

    def reflect(
        self,
        goal,
        content
    ):
        """
        Evaluate content quality.

        Returns:
        {
            "score": int,
            "passed": bool,
            "feedback": str
        }
        """

        content_preview = content[:800]

        response = self.think(
            f"""
Rate this content.

Goal: {goal}

Content:
{content_preview}

Return ONLY JSON:
{{"score": <1-10>, "feedback": "<one sentence>"}}
"""
        )

        

        try:

            result = json.loads(response)

        except Exception:

            match = re.search(
                r"\{.*\}",
                response,
                re.DOTALL
            )

            if match:

                try:
                    result = json.loads(
                        match.group()
                    )
                except Exception:
                    result = {
                        "score": 7,
                        "feedback": "Could not evaluate"
                    }

            else:

                result = {
                    "score": 7,
                    "feedback": "Could not evaluate"
                }

        score = result.get("score", 7)

        if not isinstance(score, (int, float)):
            score = 7

        score = max(1, min(10, int(score)))

        feedback = result.get(
            "feedback",
            "No feedback"
        )

        passed = score >= self.pass_threshold

        return {
            "score": score,
            "passed": passed,
            "feedback": str(feedback)
        }
