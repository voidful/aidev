import locale
import queue
import sys
import threading
import time
from itertools import cycle

import click
import git
import openai

from .config_utils import read_config, store_config

config = read_config() or {}
detected_language = locale.getdefaultlocale()[0][:2]


@click.command()
@click.option('--threshold', default=config.get('threshold', 0.5), type=float,
              help='Confidence threshold for the AI generated result (0.0 to 1.0).')
@click.option('--engine', default=config.get('engine', 'gpt-3.5-turbo'),
              help='The GPT engine to use (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4-32k").')
@click.option('--max-tokens', default=config.get('max_tokens', 300), type=int,
              help='The maximum number of tokens in the AI-generated response.')
@click.option('--language', default=config.get('language', detected_language),
              help='The output language for the AI-generated response.')
def main(threshold, engine, max_tokens, language):
    config = read_config()
    if not config:
        config = {}

    if "api_key" not in config:
        print("No API key found. Please enter your OpenAI API key:")
        api_key = input().strip()
        config["api_key"] = api_key
        store_config(config)
        print("API key stored in the config file.")
        print("Please restart the CLI tool for the changes to take effect.")
        return

    openai.api_key = config["api_key"]

    # Store the provided options in the config
    config["threshold"] = threshold
    config["engine"] = engine
    config["max_tokens"] = max_tokens
    config["language"] = language
    store_config(config)

    diff = get_git_diff()
    if not diff:
        print("No changes detected.")
        return
    mock_result = get_mock_run_result(diff, threshold, engine, language, max_tokens)
    if len(mock_result) > 0:
        print("=========")
        print(mock_result)
        print("=========")


def get_git_diff():
    repo = git.Repo('.')
    diff = repo.git.diff()
    return diff


animation_running = True


def get_mock_run_result(code, threshold, engine, language="english", max_tokens=300):
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
        f"Answer the following questions with its title, divide each answer with lines:\n"
        f"- Code Execution Test: Can the modified code run correctly? Provide a mock run and test result for the following code changes:\n"
        f"- Code Improvement: Are the changes an improvement? If not, what suggestions do you have to improve the code?\n"
        f"- Commit Message: Provide commit message based on this code change.\n"
        f"- Unit Tests: Provide example code of unit tests to cover the changes made to the code, but no need write test on documentation change:\n"
        f"Results:\n"
    )

    def _update_progress_bar():
        global animation_running
        spinner = cycle(['-', '\\', '|', '/'])
        print("\U0001F680 Running... ", end="", flush=True)
        while animation_running:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')
        sys.stdout.write(" \n")

    def _call_openai_api(prompt, engine, threshold, response_queue):
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

    response_queue = queue.Queue()
    api_call = threading.Thread(target=_call_openai_api, args=(prompt, engine, threshold, response_queue))
    api_call.start()

    progress_updater = threading.Thread(target=_update_progress_bar)
    progress_updater.start()
    api_call.join()
    progress_updater.join()

    response = response_queue.get()
    result = response.choices[0]['message']['content'].strip()
    return result


if __name__ == '__main__':
    main()
