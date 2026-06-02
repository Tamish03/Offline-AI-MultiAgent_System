from pathlib import Path


class FolderSearch:

    def search(
        self,
        folder
    ):

        folder_path = Path(
            folder
        )

        if not folder_path.exists():

            return []

        files = []

        for item in folder_path.rglob("*"):

            if item.is_file():

                files.append(
                    str(item)
                )

        return files