# helpers.py
import queue
import sys
import threading
import time
from itertools import cycle
from typing import Optional

import git
import openai


def get_git_diff() -> Optional[str]:
    repo = git.Repo('.')

    diff_cached = repo.git.diff('--cached', diff_algorithm='minimal')

    if not diff_cached:
        diff_working_dir = repo.git.diff(diff_algorithm='minimal')
        return diff_working_dir
    else:
        return diff_cached


animation_running = True


def _update_progress_bar() -> None:
    global animation_running
    spinner = cycle(['-', '\\', '|', '/'])
    print("\U0001F680 Running... ", end="", flush=True)
    while animation_running:
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    sys.stdout.write(" \n")


def _call_openai_api(prompt: str, engine: str, threshold: float, language: str, max_tokens: int,
                     response_queue: queue.Queue) -> None:
    global animation_running
    response = openai.ChatCompletion.create(
        model=engine,
        messages=[
            {"role": "system",
             "content": "You are a helpful code assistant."
                        f"You need to generate Results using the following language {language}"},
            {"role": "user",
             "content": f"You need to generate Results using the following language {language}: {prompt}"},
        ],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=threshold,
    )
    response_queue.put(response)
    animation_running = False


def get_mock_run_result(code: str, threshold: float, engine: str, language: str = "english",
                        max_tokens: int = 300) -> str:
    if engine == "gpt-3.5-turbo":
        MAX_INPUT_LENGTH = 3796  # preserve 300 char for response
    elif engine == "gpt-4":
        MAX_INPUT_LENGTH = 7892  # preserve 300 char for response
    elif engine == "gpt-4-32k":
        MAX_INPUT_LENGTH = 32468  # preserve 300 char for response
    else:
        MAX_INPUT_LENGTH = 3000

    if len(code) > MAX_INPUT_LENGTH:
        print(f"Warning: Code change is too extensive ({len(code)} characters) for AI to handle. \n"
              f"Please consider breaking your changes into smaller commits to less than {MAX_INPUT_LENGTH} characters.")
        return ""
    prompt = (
        f"Given the following code changes:\n\n{code}\n\n"
        f"Answer the following questions with its title and keep it short, divide each answer with lines:\n"
        f"- Code Execution Test: Can the modified code run correctly? Provide a mock run and test result for the following code changes:\n"
        f"- Code Improvement: Are the changes an improvement? If not, what suggestions do you have to improve the code?\n"
        f"- Commit Message: Provide a commit message following the AngularJS Git Commit Guidelines with type, scope (optional) and subject. Use imperative, present tense, and do not capitalize the first letter of the subject or end it with a period.\n"
        f"- Unit Tests: Provide example code of unit tests to cover the changes made to the code, but no need write test on documentation change:\n"
        f"Results:\n"
    )

    response_queue = queue.Queue()
    api_call = threading.Thread(target=_call_openai_api,
                                args=(prompt, engine, threshold, language, max_tokens, response_queue))
    api_call.start()

    progress_updater = threading.Thread(target=_update_progress_bar)
    progress_updater.start()
    api_call.join()
    progress_updater.join()

    response = response_queue.get()
    result = response.choices[0]['message']['content'].strip()
    return result


def assert_git_repo() -> None:
    try:
        git.Repo('.', search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        raise Exception("The current directory must be a Git repository!")
