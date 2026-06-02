from pathlib import Path
from datetime import datetime


class OutputManager:

    def __init__(
        self,
        output_dir="data/outputs"
    ):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_markdown(
        self,
        title,
        content
    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"{timestamp}_{title}.md"
        )

        filepath = (
            self.output_dir / filename
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(content)

        return str(filepath)