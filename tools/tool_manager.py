from tools.file_reader import FileReader
from tools.file_writer import FileWriter
from tools.folder_search import FolderSearch
from tools.python_executor import PythonExecutor
from tools.grep_search import GrepSearch


class ToolManager:

    def __init__(self):
        self.reader = FileReader()
        self.writer = FileWriter()
        self.searcher = FolderSearch()
        self.python_executor = PythonExecutor()
        self.grep = GrepSearch()

    def read_file(
        self,
        filepath
    ):
        return (
            self.reader
            .read_file(filepath)
        )

    def write_file(
        self,
        filepath,
        content
    ):
        return (
            self.writer
            .write_file(
                filepath,
                content
            )
        )

    def search_folder(
        self,
        folder
    ):
        return (
            self.searcher
            .search(folder)
        )

    def execute_python(
        self,
        code
    ):
        return (
            self.python_executor
            .execute(code)
        )

    def grep_search(
        self,
        query,
        folder="."
    ):
        return (
            self.grep
            .search(query, folder)
        )