import re


class ToolParser:

    def extract_file_path(
        self,
        goal
    ):
        """
        Extract filepath from tool request.
        Strips surrounding quotes or backticks.
        """
        match = re.search(
            r"(?:read file|open file)\s+(.+)",
            goal,
            re.IGNORECASE
        )

        if match:
            path = match.group(1).strip()
            # Strip quotes and backticks
            path = path.strip("\"'`")
            return path

        return None

    def extract_python_code(
        self,
        goal
    ):
        """
        Extract Python code from tool request.
        Cleans markdown code fences (```python ... ```).
        """
        # First check for code inside triple backticks
        code_block_match = re.search(
            r"```(?:python)?\n?(.*?)\n?```",
            goal,
            re.DOTALL | re.IGNORECASE
        )
        if code_block_match:
            return code_block_match.group(1).strip()

        # Fallback to matching run python / execute code prefix
        match = re.search(
            r"(?:run python|execute code)\s+(.+)",
            goal,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            code = match.group(1).strip()
            # Clean leading/trailing fences if they got partially matched
            code = re.sub(r"^```(?:python)?\n?|\n?```$", "", code).strip()
            return code

        return None

    def extract_write_file_data(self, goal):
        """
        Extract target path and code/text payload for WRITE_FILE.
        Returns (filepath, code/text) or (None, None).
        """
        match = re.search(
            r"(?:write file|create file|save file)\s+([^\s\n\r]+)",
            goal,
            re.IGNORECASE
        )
        if not match:
            return None, None
        filepath = match.group(1).strip().strip("\"'`")

        # Extract content payload - look for triple backticks first
        code = self.extract_python_code(goal)
        if not code:
            # Fallback to looking for content/code label
            content_match = re.search(
                r"(?:code|content|text)\s+(.+)",
                goal,
                re.IGNORECASE | re.DOTALL
            )
            if content_match:
                code = content_match.group(1).strip()
            else:
                # Get everything after filepath
                parts = re.split(re.escape(match.group(1)), goal, 1)
                if len(parts) > 1:
                    code = parts[1].strip()
                    code = re.sub(r"^(?:with\s+)?(?:code|content|text)?\s*", "", code, flags=re.IGNORECASE).strip()
        
        return filepath, code

    def extract_grep_search_data(self, goal):
        """
        Extract search query and target folder for GREP_SEARCH.
        Returns (query, folder).
        """
        query = None
        folder = "."
        
        match = re.search(
            r"(?:grep search|find text|search text|search inside)\s+(.+)",
            goal,
            re.IGNORECASE
        )
        if match:
            full_match = match.group(1).strip()
            in_match = re.search(r"(.+)\s+in\s+([^\s]+)$", full_match, re.IGNORECASE)
            if in_match:
                query = in_match.group(1).strip().strip("\"'`")
                folder = in_match.group(2).strip().strip("\"'`")
            else:
                query = full_match.strip().strip("\"'`")
        
        return query, folder