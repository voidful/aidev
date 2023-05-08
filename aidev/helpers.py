import queue
import sys
import threading
import time
from contextlib import contextmanager
from enum import Enum
from itertools import cycle
from typing import Optional

import git
import openai


class ResponseType(Enum):
    SIMPLE = "simple"
    EXECUTION_TEST = "execution_test"
    CODE_IMPROVEMENT = "code_improvement"
    UNIT_TESTS = "unit_tests"


def assert_git_repo() -> None:
    try:
        git.Repo('.', search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        raise Exception("The current directory must be a Git repository!")


def get_git_diff() -> Optional[str]:
    repo = git.Repo('.')

    diff_cached = repo.git.diff('--cached', diff_algorithm='minimal')

    if not diff_cached:
        diff_working_dir = repo.git.diff(diff_algorithm='minimal')
        return diff_working_dir
    else:
        return diff_cached


@contextmanager
def animation_status(status: bool):
    global animation_running
    animation_running = status
    try:
        yield
    finally:
        animation_running = not status


def update_spinner_animation():
    spinner = cycle(['-', '\\', '|', '/'])
    print("\U0001F680 Running... ", end="", flush=True)
    while animation_running:
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    sys.stdout.write(" \n")


def call_openai_api(prompt: str, engine: str, threshold: float, language: str, max_tokens: int,
                    response_queue: queue.Queue) -> None:
    print("========================================")
    with animation_status(True):
        response = openai.ChatCompletion.create(
            model=engine,
            messages=[
                {"role": "system",
                 "content": f"You are a helpful code assistant. Answer with language: {language}"},
                {"role": "user",
                 "content": f"{prompt}"}
            ],
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=threshold,
        )
    response_queue.put(response)


def input_length_validation(code: str, max_input_length: int) -> bool:
    if len(code) > max_input_length:
        print(f"Warning: Code change is too extensive ({len(code)} characters) for AI to handle. \n"
              f"Please consider breaking your changes into smaller commits to less than {max_input_length} characters.")
        return False
    return True


def get_ai_response(code: str, response_type: ResponseType, threshold: float, engine: str, language: str = "english",
                    max_tokens: int = 300) -> str:
    max_input_lengths = {
        "gpt-3.5-turbo": 3796,
        "gpt-4": 7892,
        "gpt-4-32k": 32468,
    }
    max_input_length = max_input_lengths.get(engine, 3000)

    if not input_length_validation(code, max_input_length):
        return ""

    prompt_template = build_prompt_template(response_type)
    prompt = prompt_template.format(code=code)
    response_queue = queue.Queue()
    api_call = threading.Thread(target=call_openai_api,
                                args=(prompt, engine, threshold, language, max_tokens, response_queue))
    api_call.start()

    progress_updater = threading.Thread(target=update_spinner_animation)
    progress_updater.start()
    api_call.join()
    progress_updater.join()

    response = response_queue.get()
    response_text = response.choices[0]['message']['content'].strip().replace("\n\n", "\n")
    return response_text


def build_prompt_template(response_type: ResponseType) -> str:
    if response_type == ResponseType.SIMPLE:
        return (
            f"Given the following code changes:\n{{code}}\n"
            f"Answer the following questions with its title and keep it as short as possible:\n"
            f"- Commit Message: Provide a commit message, format it inside $ and following the AngularJS Git Commit Guidelines with type, scope (optional) and subject. Use imperative, present tense, and do not capitalize the first letter of the subject or end it with a period.\n"
            f"- Code Execution Test: if they can run correctly or not? \n"
            f"- Code Improvement: if they have further improvement or not?\n"
            f"- Unit Tests: if unit tests are needed or not?\n"
            f"Results:\n"
        )
    elif response_type == ResponseType.EXECUTION_TEST:
        return (
            f"Given the following code changes:\n{{code}}\n"
            f"Answer the following questions with its title:\n"
            f"- Code Execution Test: Provide a mock run and some test result for the following code changes. \n"
            f"Results:\n"
        )
    elif response_type == ResponseType.CODE_IMPROVEMENT:
        return (
            f"Given the following code changes:\n{{code}}\n"
            f"Answer the following questions with its title:\n"
            f"- Code Improvement: Are the changes an improvement? If not, what suggestions do you have to improve the code? \n"
            f"Results:\n"
        )
    elif response_type == ResponseType.UNIT_TESTS:
        return (
            f"Given the following code changes:\n{{code}}\n"
            f"Answer the following questions with its title:\n"
            f"- Unit Tests: Provide example code of unit tests to cover the changes made to the code, but no need write test on documentation change.\n"
            f"Results:\n"
        )
    else:
        raise ValueError("Invalid response_type")


def get_ai_run_result(code: str, threshold: float, engine: str, language: str = "english",
                      max_tokens: int = 300) -> str:
    return get_ai_response(code, ResponseType.SIMPLE, threshold, engine, language, max_tokens)


def get_code_execution_test_detail(code: str, threshold: float, engine: str, language: str = "english",
                                   max_tokens: int = 300) -> str:
    return get_ai_response(code, ResponseType.EXECUTION_TEST, threshold, engine, language, max_tokens)


def get_code_improvement_detail(code: str, threshold: float, engine: str, language: str = "english",
                                max_tokens: int = 300) -> str:
    return get_ai_response(code, ResponseType.CODE_IMPROVEMENT, threshold, engine, language, max_tokens)


def get_unit_tests_detail(code: str, threshold: float, engine: str, language: str = "english",
                          max_tokens: int = 300) -> str:
    return get_ai_response(code, ResponseType.UNIT_TESTS, threshold, engine, language, max_tokens)
