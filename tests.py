"""Unit tests for AI agent."""

# get_files_info("calculator", ".")
# get_files_info("calculator", "pkg")
# get_files_info("calculator", "/bin")
# get_files_info("calculator", "../")

# get_file_content("calculator", "lorem.txt")
# get_file_content("calculator", "main.py")
# get_file_content("calculator", "pkg/calculator.py")
# get_file_content("calculator", "/bin/cat")

from functions.files import write_file

for result in [
    write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"),
    write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"),
    write_file("calculator", "/tmp/temp.txt", "this should not be allowed"),
]:
    print(result)
