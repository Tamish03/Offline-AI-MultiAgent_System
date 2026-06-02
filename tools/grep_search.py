import os
import re
from pathlib import Path


class GrepSearch:
    """
    Recursive text search (grep) utility.
    Searches inside text files in a target directory.
    """

    def __init__(self, ignore_folders=None):
        if ignore_folders is None:
            self.ignore_folders = {
                "venv", ".git", "__pycache__", "node_modules", 
                ".gemini", "data/memory"
            }
        else:
            self.ignore_folders = set(ignore_folders)

    def search(self, query, folder=".", max_results=50):
        if not query:
            return "Error: No search query provided."

        target_dir = Path(folder)
        if not target_dir.exists() or not target_dir.is_dir():
            return f"Error: Target directory '{folder}' does not exist or is not a directory."

        matches = []
        try:
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            
            for root, dirs, files in os.walk(target_dir):
                # Skip hidden and ignored folders
                dirs[:] = [d for d in dirs if d not in self.ignore_folders and not d.startswith(".")]
                
                parts = Path(root).parts
                if any(ignored in parts for ignored in self.ignore_folders):
                    continue
                
                for file in files:
                    file_path = Path(root) / file
                    
                    if file_path.suffix.lower() in {
                        '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', 
                        '.gz', '.db', '.sqlite', '.exe', '.dll', '.so', '.pyc'
                    }:
                        continue
                        
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            for line_num, line in enumerate(f, start=1):
                                if pattern.search(line):
                                    # Try to make path relative, else use absolute/relative string
                                    try:
                                        rel_path = file_path.relative_to(target_dir)
                                    except ValueError:
                                        rel_path = file_path
                                    matches.append(f"{rel_path}:{line_num}: {line.strip()}")
                                    if len(matches) >= max_results:
                                        break
                    except Exception:
                        continue
                        
                    if len(matches) >= max_results:
                        break
                if len(matches) >= max_results:
                    break
        except Exception as e:
            return f"Error executing grep search: {e}"

        if not matches:
            return f"No matches found for '{query}' in '{folder}'."

        result = f"Grep Results for '{query}' in '{folder}' (showing up to {max_results} matches):\n\n"
        result += "\n".join(matches)
        if len(matches) >= max_results:
            result += "\n\n... [Truncated: reached maximum result count]"
        return result
