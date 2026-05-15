"""Files related functions."""

import os
import subprocess

from functions.constants import MAX_CHARS, ErrorSuffixes


def check_valid_path(working_directory: str, file_path: str) -> tuple[str, bool]:
    """Resolve a path and check whether it escapes the working directory.

    Args:
        working_directory (str): Absolute or relative path to the sandbox root.
        file_path (str): Path requested by the agent, relative to working_directory.

    Returns:
        tuple[str, bool]: A tuple of (resolved_absolute_path, is_outside) where
        is_outside is True when the resolved path falls outside working_directory.
    """
    wd = os.path.abspath(working_directory)
    fp = os.path.join(wd, file_path)

    return fp, not os.path.abspath(fp).startswith(wd)


def get_file_content(working_directory: str, file_path: str) -> str:
    """Read and return the content of a file within the working directory.

    Args:
        working_directory (str): Sandbox root directory.
        file_path (str): Path to the file, relative to working_directory.

    Returns:
        str: File contents, truncated to MAX_CHARS with a notice if large,
        or an error message prefixed with "Error:".
    """
    fp, error = check_valid_path(working_directory, file_path)
    if error:
        return (
            f'Error: Cannot read "{file_path}" '
            f"{ErrorSuffixes.OUTSIDE_WORKING_DIR.value}"
        )

    if not os.path.isfile(fp):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
            if len(content) > MAX_CHARS:
                return (
                    content[:MAX_CHARS]
                    + f'\n[...File "{file_path}" truncated at 10000 characters]'
                )
            return content

    except OSError:
        return f'Error: Error when reading "{file_path}"'


def get_dir_size(path: str = ".") -> int:
    """Recursively compute the total byte size of a directory.

    Args:
        path (str): Directory path to measure.

    Returns:
        int: Total size in bytes of all files within the directory tree.
    """
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def get_files_info(working_directory: str, directory: str) -> str:
    """List files and subdirectories within a directory, with sizes.

    Args:
        working_directory (str): Sandbox root directory.
        directory (str): Directory to inspect, relative to working_directory.

    Returns:
        str: A newline-delimited string of name/size/is_dir entries prefixed
        with a success line, or an error message prefixed with "Error:".
    """
    dp, error = check_valid_path(working_directory, directory)
    if error:
        return (
            f'Error: Cannot list "{directory}" '
            f"{ErrorSuffixes.OUTSIDE_WORKING_DIR.value}"
        )

    if not os.path.isdir(dp):
        return f'Error: "{dp}" is not a directory'

    result = f'Success: "{directory}" is within the working directory\n'
    with os.scandir(dp) as it:
        for item in it:
            size = os.path.getsize(item) if item.is_file() else get_dir_size(item.path)
            result += f"{item.name}: file_size={size}, is_dir={str(item.is_dir())}\n"

    return result


def write_file(working_directory: str, file_path: str, content: str) -> str:
    """Write content to a file within the working directory.

    Creates any missing parent directories. Overwrites an existing file.

    Args:
        working_directory (str): Sandbox root directory.
        file_path (str): Destination path, relative to working_directory.
        content (str): Text to write to the file.

    Returns:
        str: A success message with character count, or an error message
        prefixed with "Error:".
    """
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


def run_python_file(working_directory: str, file_path: str) -> str:
    """Execute a Python file as a subprocess within the working directory.

    Args:
        working_directory (str): Sandbox root directory used as the subprocess cwd.
        file_path (str): Path to the .py file, relative to working_directory.

    Returns:
        str: Combined stdout/stderr output and exit code, or an error message
        prefixed with "Error:".
    """
    fp, error = check_valid_path(working_directory, file_path)
    if error:
        return (
            f'Error: Cannot execute "{file_path}" '
            f"{ErrorSuffixes.OUTSIDE_WORKING_DIR.value}"
        )

    if not os.path.exists(fp):
        return f'Error: File "{file_path}" not found.'

    if not fp.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        result = subprocess.run(  # noqa: S603
            ["python", fp],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=os.path.abspath(working_directory),
        )
        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if result.returncode:
            output.append(f"Process exited with code {result.returncode}")

        return "\n".join(output) if output else "No output produced."

    except Exception as err:  # pylint: disable=broad-except
        return f"Error: executing Python file: {err}"
