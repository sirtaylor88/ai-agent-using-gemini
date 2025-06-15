"""Files related functions."""

import os

from functions.constants import MAX_CHARS, ErrorSuffixes


def check_valid_path(working_directory: str, file_path: str) -> tuple[str, bool]:
    """Check if file path is valid."""
    wd = os.path.abspath(working_directory)
    fp = os.path.join(wd, file_path)

    return fp, not os.path.abspath(fp).startswith(wd)


def get_file_content(working_directory: str, file_path: str):
    """Get the content of a file."""

    fp, error = check_valid_path(working_directory, file_path)
    if error:
        return (
            f'Error: Cannot read "{file_path}" '
            f"{ErrorSuffixes.OUTSIDE_WORKING_DIR.value}"
        )

    if not os.path.isfile(fp):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        count = 0
        chunk = ""
        result = ""
        with open(fp, "r", encoding="utf-8") as f:
            while True:
                result = chunk
                chunk = f.read(MAX_CHARS)
                count += 1
                if count == 2:
                    result += f'\n[...File "{file_path}" truncated at 10000 characters]'
                    break
        return result

    except OSError:
        return f'Error: Error when reading "{file_path}"'


def get_dir_size(path: str = "."):
    """Return directory size."""
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def get_files_info(working_directory: str, directory: str) -> str:
    """Get useful info from files in a directory."""

    dp, error = check_valid_path(working_directory, directory)
    if error:
        return (
            f'Error: Cannot list "{directory}" '
            f"{ErrorSuffixes.OUTSIDE_WORKING_DIR.value}"
        )

    if not os.path.isdir(dp):
        return f'Error: "{dp}" is not a directory'

    result = ""
    with os.scandir(dp) as it:
        for item in it:
            size = os.path.getsize(item) if item.is_file() else get_dir_size(item)
            result += f"{item.name}: file_size={size}, is_dir={str(item.is_dir())}\n"

    return result


def write_file(working_directory: str, file_path: str, content: str):
    """Write a file."""

    fp, error = check_valid_path(working_directory, file_path)
    if error:
        return (
            f'Error: Cannot write to "{file_path}" '
            f"{ErrorSuffixes.OUTSIDE_WORKING_DIR.value}"
        )

    os.makedirs(os.path.dirname(fp), exist_ok=True)

    try:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )

    except OSError:
        return f'Error: Error when writing "{file_path}"'
