from pathlib import Path


class FileReader:

    def read_file(
        self,
        filepath
    ):

        path = Path(
            filepath
        )

        if not path.exists():

            return (
                f"File not found: "
                f"{filepath}"
            )

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                return file.read()

        except Exception as e:

            return str(e)