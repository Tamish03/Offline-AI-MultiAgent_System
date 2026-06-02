from agents.base_agent import BaseAgent
from tools.tool_manager import ToolManager


class ToolAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Tool Agent",
            role="Tool Specialist",
            system_prompt="""
You decide which tool should be used.

Available tools:

- read_file
- write_file
- search_folder
- execute_python
- grep_search

Return only the tool name.
"""
        )

        self.tools = ToolManager()

    def search_folder(
        self,
        folder
    ):

        return (
            self.tools
            .search_folder(
                folder
            )
        )

    def read_file(
        self,
        filepath
    ):

        return (
            self.tools
            .read_file(
                filepath
            )
        )

    def execute_python(
        self,
        code
    ):

        return (
            self.tools
            .execute_python(
                code
            )
        )

    def write_file(
        self,
        filepath,
        content
    ):

        return (
            self.tools
            .write_file(
                filepath,
                content
            )
        )

    def grep_search(
        self,
        query,
        folder="."
    ):

        return (
            self.tools
            .grep_search(
                query,
                folder
            )
        )