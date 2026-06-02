class ToolMemory:

    def __init__(self):

        self.last_tool = None

        self.last_result = None

    def save(
        self,
        tool_name,
        result
    ):

        self.last_tool = tool_name

        self.last_result = result

    def get_last_tool(self):

        return self.last_tool

    def get_last_result(self):

        return self.last_result

    def clear(self):

        self.last_tool = None

        self.last_result = None