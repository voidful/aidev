import locale
import subprocess

import click
import openai
from bullet import Bullet

from aidev.helpers import get_git_diff, get_ai_run_result, get_code_execution_test_detail, get_code_improvement_detail, \
    get_unit_tests_detail
from .config_utils import read_config, store_config

config = read_config() or {}
detected_language = locale.getdefaultlocale()[0][:2]


@click.command()
@click.option('--threshold', default=config.get('threshold', 0.3), type=float,
              help='Confidence threshold for the AI generated result (0.0 to 1.0).')
@click.option('--engine', default=config.get('engine', 'gpt-3.5-turbo'),
              help='The GPT engine to use (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4-32k").')
@click.option('--max-tokens', default=config.get('max_tokens', 1024), type=int,
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
    response_text = get_ai_run_result(diff, threshold, engine, language, max_tokens)
    while True:
        cli = Bullet(choices=["Create a commit",
                              "Run Code Execution Test",
                              "Give detailed Code Improvement",
                              "Create a unit test for this change",
                              "Exit"],
                     prompt=f"{response_text}\nSelect an action: ",
                     bullet=">")

        action = cli.launch()

        if action == "Create a commit":
            commit_msg = " ".join(response_text.split("$")[1:2]).strip()
            print(f"Commit message: {commit_msg}")
            confirm_commit = input("Do you want to commit these changes? (y/n): ").lower() == 'y'
            if confirm_commit:
                try:
                    subprocess.run(["git", "add", "-A"], check=True)
                    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                    print("Commit created successfully.")
                    confirm_push = input("Do you want to push the commit? (y/n): ").lower() == 'y'
                    if confirm_push:
                        try:
                            subprocess.run(["git", "push"], check=True)
                            print("Commit pushed successfully.")
                        except subprocess.CalledProcessError as e:
                            print(f"Error pushing commit: {e}")
                except subprocess.CalledProcessError as e:
                    print(f"Error creating commit: {e}")
        elif action == "Run Code Execution Test":
            response_text = "Code Execution Test\n"
            response_text += get_code_execution_test_detail(diff, threshold, engine, language, max_tokens)
        elif action == "Give detailed Code Improvement":
            response_text = "Code Improvement\n"
            response_text += get_code_improvement_detail(diff, threshold, engine, language, max_tokens)
        elif action == "Create a unit test for this change":
            response_text = "Unit Test\n"
            response_text += get_unit_tests_detail(diff, threshold, engine, language, max_tokens)
        elif action == "Exit":
            break