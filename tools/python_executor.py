import subprocess
import tempfile
import os


class PythonExecutor:

    def execute(
        self,
        code
    ):

        try:

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8"
            ) as file:

                file.write(code)

                temp_file = file.name

            result = subprocess.run(
                [
                    "python",
                    temp_file
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            os.remove(
                temp_file
            )

            if result.returncode == 0:

                return result.stdout

            return result.stderr

        except Exception as e:

            return str(e)