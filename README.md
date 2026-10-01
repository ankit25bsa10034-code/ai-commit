# AI Git Commit Message Generator

A small Python command-line tool that reads your staged git changes, asks OpenAI to write one
[conventional commit](https://www.conventionalcommits.org/) message, and commits it if you agree.

Example messages it can produce:

```
feat: add user authentication
fix: handle empty input
refactor: simplify API client
```

## What you need

- Python 3.9 or newer
- Git installed and available in your terminal
- An OpenAI API key

## Setup (Windows, macOS, Linux)

1. Open a terminal in the project folder.

2. (Recommended) Create and activate a virtual environment.

   Windows (PowerShell):

   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

   macOS / Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the packages:

   ```
   pip install -r requirements.txt
   ```

4. Create a file named `.env` in the same folder as `main.py` and add your key:

   ```
   OPENAI_API_KEY=your_key_here
   ```

   The `.env` file is listed in `.gitignore`, so it will not be committed. Never share it.

## How to use it

1. Go to the git repository you want to commit in.
2. Stage your changes:

   ```
   git add .
   ```

3. Run the tool, using the path to `main.py`:

   ```
   python main.py
   ```

   If you are in a different folder, give the full path, for example `python C:\tools\ai-commit-generator\main.py`.

4. The tool shows a suggested message and asks:

   ```
   Commit with this message? [Y/n]
   ```

   - Press Enter or type `y` to run `git commit -m "..."`.
   - Type `n` to exit without committing.

## How it works

1. Runs `git diff --cached` to read your staged changes.
2. Sends the diff to the OpenAI Responses API using the model `gpt-5.6-luna`.
3. Shows you the generated message.
4. Commits only if you confirm.

Very large diffs are cut off at 20,000 characters before being sent.

## Common errors

| Message | What to do |
| --- | --- |
| `OPENAI_API_KEY is missing` | Create the `.env` file described in step 4 of Setup. |
| `no staged changes found` | Run `git add <file>` first. |
| `git was not found` | Install Git and restart your terminal. |
| `Are you inside a git repository?` | Run the tool from inside a folder that has a `.git` directory. |
| `the OpenAI request failed` | Check your API key, internet connection, and that your account can use the model. |

## License

MIT. See the `LICENSE` file. Replace "Your Name" in it with your own name.
