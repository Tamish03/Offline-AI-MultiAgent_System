class ToolRouter:

    def classify(
        self,
        goal
    ):

        goal = goal.lower()

        if (
            "read file" in goal
            or "open file" in goal
        ):

            return "READ_FILE"

        if (
            "write file" in goal
            or "create file" in goal
            or "save file" in goal
        ):

            return "WRITE_FILE"

        if (
            "search folder" in goal
            or "list files" in goal
        ):

            return "SEARCH_FOLDER"

        if (
            "grep search" in goal
            or "find text" in goal
            or "search text" in goal
            or "search inside" in goal
        ):

            return "GREP_SEARCH"

        if (
            "run python" in goal
            or "execute code" in goal
        ):

            return "EXECUTE_PYTHON"

        return None