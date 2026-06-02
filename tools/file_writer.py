from pathlib import Path


class FileWriter:

    def write_file(
        self,
        filepath,
        content
    ):

        path = Path(
            filepath
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                content
            )

        return (
            f"Saved: {filepath}"
        )