"""Main app."""

import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.constants import SYSTEM_PROMPT
from utils import call_function

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description=(
        "Lists files in the specified directory along with their sizes, constrained "
        "to the working directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The directory to list files from, relative to the working "
                    "directory. If not provided, lists files in the working "
                    "directory itself."
                ),
            ),
        },
        required=["directory"],
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=(
        "Read file content from the specified file path, constrained to the working "
        "directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The path to the file, relative to the working directory."
                ),
            ),
        },
        required=["file_path"],
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description=(
        "Run the Python file from the specified file path, constrained to the working "
        "directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The path to the file, relative to the working directory."
                ),
            ),
        },
        required=["file_path"],
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description=(
        "Write content to the file with the specified file path, constrained to "
        "the working directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The path to the file, relative to the working directory."
                ),
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description=("Content to write to the file."),
            ),
        },
        required=["file_path", "content"],
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)


def main():
    """Main app."""
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <sentence> --<option>")
        sys.exit(1)

    user_prompt = sys.argv[1]
    verbose_mode = len(sys.argv) == 3 and sys.argv[2] == "--verbose"

    if verbose_mode:
        print("User prompt:", user_prompt)

    count = 0
    messages = [
        types.Content(
            role="user",
            parts=[types.Part(text=user_prompt)],
        ),
    ]
    while count < 20:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=SYSTEM_PROMPT,
            ),
        )

        messages.extend(candidate.content for candidate in response.candidates)
        if not response.function_calls:
            print(response.text)
            break

        for function_call_part in response.function_calls:
            function_call_result = call_function(
                function_call_part, verbose=verbose_mode
            )
            messages.append(function_call_result)
            try:
                content = function_call_result.parts[0].function_response.response
            except Exception as exc:
                raise AttributeError("Unknow error") from exc

            if verbose_mode:
                print(f"-> {content}")

        count += 1

    if verbose_mode:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)
    sys.exit(0)


main()
