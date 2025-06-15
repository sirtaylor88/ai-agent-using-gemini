"""Unit tests for AI agent."""

# get_files_info("calculator", ".")
# get_files_info("calculator", "pkg")
# get_files_info("calculator", "/bin")
# get_files_info("calculator", "../")

# get_file_content("calculator", "lorem.txt")
# get_file_content("calculator", "main.py")
# get_file_content("calculator", "pkg/calculator.py")
# get_file_content("calculator", "/bin/cat")

# write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"),
# write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"),
# write_file("calculator", "/tmp/temp.txt", "this should not be allowed"),

from functions.files import run_python_file

for result in [
    run_python_file("calculator", "main.py"),
    run_python_file("calculator", "tests.py"),
    run_python_file("calculator", "../main.py"),
    run_python_file("calculator", "nonexistent.py"),
]:
    print(result)
