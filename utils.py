"""Useful functions."""

from google.genai import types

from functions.files import (
    get_file_content,
    get_files_info,
    run_python_file,
    write_file,
)


def call_function(
    function_call_part: types.FunctionCall, verbose: bool = False
) -> types.Content:
    """Dispatch a Gemini function call to its Python implementation.

    Injects ``./calculator`` as the working directory for all tool functions.
    Returns an error response for unknown function names.

    Args:
        function_call_part (types.FunctionCall): The FunctionCall from a Gemini response.
        verbose (bool): If True, print the full function name and arguments;
            otherwise print a compact one-liner.

    Returns:
        types.Content: A Content object with role "tool" containing the function
        response.
    """
    function_name = function_call_part.name
    function_args = function_call_part.args
    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    functions = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }
    if function_name in functions:
        function_result = functions[function_name]("./calculator", **function_args)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"error": f"Unknown function: {function_name}"},
            )
        ],
    )
