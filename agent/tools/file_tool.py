import os


def read_file(file_path: str) -> str:

    if not os.path.exists(file_path):
        return "File not found."

    if not os.path.isfile(file_path):
        return "The provided path is not a file."

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    except Exception as e:
        return f"Could not read the file: {e}"