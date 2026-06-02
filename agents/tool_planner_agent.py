import json
import re

from agents.base_agent import BaseAgent


class ToolPlannerAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Tool Planner Agent",
            role="Tool Selector",
            system_prompt="""
You decide whether a tool is needed.

Available tools:

SEARCH_FOLDER
READ_FILE
EXECUTE_PYTHON

Return ONLY valid JSON.

Examples:

{
    "tool":"SEARCH_FOLDER",
    "folder":"data"
}

{
    "tool":"READ_FILE",
    "filepath":"data/test.txt"
}

{
    "tool":"NONE"
}
"""
        )

    def decide_tool(
        self,
        goal
    ):
        """
        Deterministic parser for tools.
        Bypasses LLM entirely to achieve zero latency and 100% reliability.
        """
        from core.tool_router import ToolRouter
        from core.tool_parser import ToolParser

        router = ToolRouter()
        parser = ToolParser()

        tool = router.classify(goal)

        if tool == "READ_FILE":
            filepath = parser.extract_file_path(goal)
            return {
                "tool": "READ_FILE",
                "filepath": filepath
            }

        elif tool == "SEARCH_FOLDER":
            folder = "data"
            match = re.search(
                r"(?:search folder|list files)\s+(.+)",
                goal,
                re.IGNORECASE
            )
            if match:
                folder = match.group(1).strip().strip("\"'`")
            return {
                "tool": "SEARCH_FOLDER",
                "folder": folder
            }

        elif tool == "EXECUTE_PYTHON":
            code = parser.extract_python_code(goal)
            return {
                "tool": "EXECUTE_PYTHON",
                "code": code
            }

        return {
            "tool": "NONE"
        }