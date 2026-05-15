"""Tests for functions.files module."""

from pathlib import Path

from functions.files import (
    check_valid_path,
    get_file_content,
    get_files_info,
    run_python_file,
    write_file,
)


class TestCheckValidPath:
    """Tests for check_valid_path."""

    def test_returns_resolved_absolute_path(self, tmp_path: Path) -> None:
        """Resolved path is an absolute path under the working directory."""
        fp, _ = check_valid_path(str(tmp_path), "file.txt")
        assert fp == str(tmp_path / "file.txt")

    def test_nested_path_is_valid(self, tmp_path: Path) -> None:
        """A path within a subdirectory is not flagged as outside."""
        _, is_outside = check_valid_path(str(tmp_path), "subdir/file.txt")
        assert not is_outside

    def test_parent_traversal_is_outside(self, tmp_path: Path) -> None:
        """../ traversal is detected as escaping the working directory."""
        _, is_outside = check_valid_path(str(tmp_path), "../outside.txt")
        assert is_outside

    def test_absolute_path_outside_is_detected(self, tmp_path: Path) -> None:
        """An absolute path outside the sandbox is flagged."""
        _, is_outside = check_valid_path(str(tmp_path), "/etc/passwd")
        assert is_outside


class TestGetFilesInfo:
    """Tests for get_files_info."""

    def test_lists_files_in_directory(self, tmp_path: Path) -> None:
        """File names appear in the output for a valid directory."""
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        result = get_files_info(str(tmp_path), ".")
        assert "a.txt" in result
        assert "b.txt" in result
        assert result.startswith("Success")

    def test_subdirectory_can_be_listed(self, tmp_path: Path) -> None:
        """Files inside a subdirectory are listed when targeting that subdir."""
        subdir = tmp_path / "pkg"
        subdir.mkdir()
        (subdir / "module.py").write_text("")
        result = get_files_info(str(tmp_path), "pkg")
        assert "module.py" in result

    def test_path_outside_working_dir_returns_error(self, tmp_path: Path) -> None:
        """Directory traversal returns an error string."""
        result = get_files_info(str(tmp_path), "../")
        assert result.startswith("Error:")

    def test_non_directory_returns_error(self, tmp_path: Path) -> None:
        """Passing a file path instead of a directory returns an error."""
        (tmp_path / "file.txt").write_text("data")
        result = get_files_info(str(tmp_path), "file.txt")
        assert result.startswith("Error:")


class TestGetFileContent:
    """Tests for get_file_content."""

    def test_reads_file_content(self, tmp_path: Path) -> None:
        """Returns the exact text content of a file."""
        (tmp_path / "hello.txt").write_text("hello world")
        result = get_file_content(str(tmp_path), "hello.txt")
        assert result == "hello world"

    def test_nonexistent_file_returns_error(self, tmp_path: Path) -> None:
        """Returns an error for a file that does not exist."""
        result = get_file_content(str(tmp_path), "missing.txt")
        assert result.startswith("Error:")

    def test_path_outside_working_dir_returns_error(self, tmp_path: Path) -> None:
        """Returns an error when the path escapes the sandbox."""
        result = get_file_content(str(tmp_path), "/etc/passwd")
        assert result.startswith("Error:")

    def test_large_file_is_truncated(self, tmp_path: Path) -> None:
        """Files exceeding MAX_CHARS are truncated with a notice."""
        (tmp_path / "big.txt").write_text("x" * 15000)
        result = get_file_content(str(tmp_path), "big.txt")
        assert "truncated" in result
        assert result.startswith("x" * 100)
        assert len(result) < 15000


class TestWriteFile:
    """Tests for write_file."""

    def test_writes_new_file(self, tmp_path: Path) -> None:
        """Content is written and the file exists after the call."""
        result = write_file(str(tmp_path), "output.txt", "content here")
        assert "Successfully wrote" in result
        assert (tmp_path / "output.txt").read_text() == "content here"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Missing parent directories are created automatically."""
        result = write_file(str(tmp_path), "sub/dir/file.txt", "data")
        assert "Successfully wrote" in result
        assert (tmp_path / "sub" / "dir" / "file.txt").exists()

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        """An existing file is replaced with the new content."""
        (tmp_path / "file.txt").write_text("old content")
        write_file(str(tmp_path), "file.txt", "new content")
        assert (tmp_path / "file.txt").read_text() == "new content"

    def test_path_outside_working_dir_returns_error(self, tmp_path: Path) -> None:
        """Returns an error without writing when the path escapes the sandbox."""
        result = write_file(str(tmp_path), "/tmp/evil.txt", "content")  # noqa: S108
        assert result.startswith("Error:")

    def test_reports_character_count(self, tmp_path: Path) -> None:
        """Success message includes the number of characters written."""
        result = write_file(str(tmp_path), "file.txt", "hello")
        assert "5" in result


class TestRunPythonFile:
    """Tests for run_python_file."""

    def test_captures_stdout(self, tmp_path: Path) -> None:
        """stdout from the script appears in the return value."""
        (tmp_path / "hello.py").write_text('print("hello world")')
        result = run_python_file(str(tmp_path), "hello.py")
        assert "hello world" in result

    def test_captures_stderr(self, tmp_path: Path) -> None:
        """stderr from the script is included under a STDERR label."""
        (tmp_path / "err.py").write_text('import sys; sys.stderr.write("oops")')
        result = run_python_file(str(tmp_path), "err.py")
        assert "STDERR" in result
        assert "oops" in result

    def test_nonexistent_file_returns_error(self, tmp_path: Path) -> None:
        """Returns an error for a .py path that does not exist."""
        result = run_python_file(str(tmp_path), "missing.py")
        assert result.startswith("Error:")

    def test_non_python_file_returns_error(self, tmp_path: Path) -> None:
        """Returns an error when the file does not have a .py extension."""
        (tmp_path / "script.sh").write_text("#!/bin/bash")
        result = run_python_file(str(tmp_path), "script.sh")
        assert result.startswith("Error:")

    def test_path_outside_working_dir_returns_error(self, tmp_path: Path) -> None:
        """Returns an error without executing when path escapes the sandbox."""
        result = run_python_file(str(tmp_path), "../outside.py")
        assert result.startswith("Error:")

    def test_nonzero_exit_code_reported(self, tmp_path: Path) -> None:
        """A script that exits with a non-zero code reports the exit code."""
        (tmp_path / "fail.py").write_text("raise SystemExit(1)")
        result = run_python_file(str(tmp_path), "fail.py")
        assert "exit" in result.lower() or "code" in result.lower()
