import locale

import click
import openai

from aidev.helpers import get_mock_run_result, get_git_diff
from .config_utils import read_config, store_config

config = read_config() or {}
detected_language = locale.getdefaultlocale()[0][:2]


@click.command()
@click.option('--threshold', default=config.get('threshold', 0.3), type=float,
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



if __name__ == '__main__':
    main()
