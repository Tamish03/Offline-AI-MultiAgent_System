import json
import re

from agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Planner Agent",
            role="Workflow Planner",
            system_prompt="""
You are an expert workflow planner.

Break the user's goal into executable tasks.

Rules:

1. Return ONLY JSON.
2. No explanations.
3. No markdown.
4. No code fences.
5. Use only:
   - deep_research
   - write
   - review

6. Each task description must be self-contained and explicitly mention the specific main subject/topic of the goal (e.g. do not write generic tasks like "Research challenges" or "Write the report", instead write "Research challenges in learning Generative AI" or "Write the final Generative AI learning roadmap").

Example:

[
    {
        "task_type": "deep_research",
        "description": "Research the topic"
    },
    {
        "task_type": "write",
        "description": "Write a report"
    },
    {
        "task_type": "review",
        "description": "Review and improve the report"
    }
]
"""
        )

    def create_plan(
        self,
        goal
    ):

        goal_lower = goal.lower()

        

        research_keywords = [

            "research",
            "study",
            "analyze",
            "analyse",
            "investigate",
            "compare",
            "learn about",
        ]

        if any(
            keyword in goal_lower
            for keyword in research_keywords
        ):

            print(
                "\nUsing Forced Research Workflow\n"
            )

            return [

                {
                    "task_type": "deep_research",
                    "description": goal
                },

                {
                    "task_type": "write",
                    "description":
                    "Create a comprehensive report "
                    "based on the research"
                },

                {
                    "task_type": "review",
                    "description":
                    "Review and improve the report"
                }
            ]

       

        response = self.think(
            f"""
Create a workflow plan for:

{goal}

Return ONLY a JSON array.
"""
        )

        print("\nRAW PLANNER RESPONSE:\n")
        print(response)
        print("\n" + "=" * 60 + "\n")

        # Remove markdown fences

        response = re.sub(
            r"```json|```",
            "",
            response,
            flags=re.IGNORECASE
        ).strip()

        # Direct JSON parse

        try:

            plan = json.loads(
                response
            )

            if (
                isinstance(plan, list)
                and len(plan) > 0
            ):

                return self._validate_plan(plan)

        except Exception:

            pass

        # Extract JSON array from text

        match = re.search(
            r"\[\s*{.*?}\s*\]",
            response,
            re.DOTALL
        )

        if match:

            try:

                plan = json.loads(
                    match.group(0)
                )

                if (
                    isinstance(plan, list)
                    and len(plan) > 0
                ):

                    return self._validate_plan(plan)

            except Exception:

                pass


        print(
            "\nPlanner failed. Using fallback plan.\n"
        )

        return [

            {
                "task_type": "deep_research",
                "description": goal
            },

            {
                "task_type": "write",
                "description": "Create report"
            },

            {
                "task_type": "review",
                "description": "Review report"
            }
        ]

    def _validate_plan(self, plan):
        """
        Ensure plan uses valid task types.
        Replace 'research' with 'deep_research'.
        """

        valid_types = {
            "deep_research",
            "research",
            "write",
            "review"
        }

        validated = []

        for step in plan:

            task_type = step.get(
                "task_type",
                "write"
            )

            if task_type == "research":
                task_type = "deep_research"

            if task_type not in valid_types:
                task_type = "write"

            validated.append({
                "task_type": task_type,
                "description": step.get(
                    "description",
                    ""
                )
            })

        return validated
