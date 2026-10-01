"""AI Git Commit Message Generator.

Reads your staged changes (git diff --cached), asks OpenAI to write one
conventional commit message, shows it to you, and commits if you agree.
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

MODEL = "gpt-5.6-luna"

# Very large diffs can be too big to send, so we cut them off here.
MAX_DIFF_CHARS = 20000

INSTRUCTIONS = (
    "You write git commit messages. Given a git diff, reply with exactly ONE "
    "concise conventional commit message in the format 'type: description'. "
    "Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore. "
    "Use lowercase, imperative mood, no trailing period, and keep it under 72 "
    "characters. Reply with the message only - no quotes, no backticks, no "
    "explanation."
)


def load_api_key():
    """Load OPENAI_API_KEY from a .env file (never hardcoded in this code)."""
    # First look for .env next to this script, then in the current folder.
    load_dotenv(Path(__file__).resolve().parent / ".env")
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        sys.exit(
            "Error: OPENAI_API_KEY is missing.\n"
            "Create a file named .env next to main.py and add this line:\n"
            "OPENAI_API_KEY=your_key_here"
        )
    return api_key.strip()


def get_staged_diff():
    """Run 'git diff --cached' and return its output as text."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        sys.exit("Error: git was not found. Please install Git and try again.")

    if result.returncode != 0:
        sys.exit(
            "Error: could not read the git diff. "
            "Are you inside a git repository?\n" + result.stderr.strip()
        )

    diff = result.stdout.strip()
    if not diff:
        sys.exit(
            "Error: no staged changes found.\n"
            "Stage your changes first, for example: git add <file>"
        )
    return diff


def generate_commit_message(api_key, diff):
    """Send the diff to OpenAI (Responses API) and return the message."""
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n...[diff truncated]"

    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            input="Write a commit message for this diff:\n\n" + diff,
        )
    except OpenAIError as error:
        sys.exit(f"Error: the OpenAI request failed.\n{error}")

    text = (response.output_text or "").strip()
    if not text:
        sys.exit("Error: the model returned an empty message.")

    # Keep only the first line and remove quotes/backticks just in case.
    first_line = text.splitlines()[0].strip()
    return first_line.strip("`\"' ")


def commit(message):
    """Run git commit with the given message."""
    # A list of arguments (no shell) works the same on Windows, Mac and Linux.
    result = subprocess.run(["git", "commit", "-m", message])
    if result.returncode != 0:
        sys.exit("Error: git commit failed.")


def main():
    api_key = load_api_key()
    diff = get_staged_diff()

    print("Generating commit message...")
    message = generate_commit_message(api_key, diff)

    print(f"\nSuggested commit message:\n  {message}\n")

    answer = input("Commit with this message? [Y/n] ").strip().lower()
    if answer in ("", "y", "yes"):
        commit(message)
    else:
        print("Cancelled. Nothing was committed.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. Nothing was committed.")
        sys.exit(1)
