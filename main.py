"""Main app."""

import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def main():
    """Main app."""
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <sentence> --<option>")
        sys.exit(1)

    user_prompt = sys.argv[1]
    verbose_mode = len(sys.argv) == 3 and sys.argv[2] == "--verbose"

    if verbose_mode:
        print("User prompt:", user_prompt)

    messages = [
        types.Content(
            role="user",
            parts=[types.Part(text=user_prompt)],
        ),
    ]

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
    )
    print(response.text)
    if verbose_mode:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)
    sys.exit(0)


main()
