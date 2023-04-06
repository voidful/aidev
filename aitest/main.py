import click
import git
import openai

from .config_utils import read_config, store_config

config = read_config() or {}


@click.command()
@click.option('--threshold', default=config.get('threshold', 0.5), type=float,
              help='Confidence threshold for the AI generated result (0.0 to 1.0).')
@click.option('--engine', default=config.get('engine', 'gpt-3.5-turbo'),
              help='The GPT-3 engine to use (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4-32k").')
@click.option('--max-tokens', default=config.get('max_tokens', 300), type=int,
              help='The maximum number of tokens in the AI-generated response.')
@click.option('--mock-test', 'action', flag_value='mock_test',
              help='Run a mock test before committing, powered by AI (ChatGPT/GPT-4).')
@click.option('--suggestion', 'action', flag_value='suggestion',
              help='Provide suggestions before committing, powered by AI (ChatGPT/GPT-4).')
@click.option('--unit-test', 'action', flag_value='unit_test',
              help='Write unit tests for code changes before committing, powered by AI (ChatGPT/GPT-4).')
def main(threshold, engine, max_tokens, action):
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
    store_config(config)

    diff = get_git_diff()
    if not diff:
        print("No changes detected.")
        return

    mock_result = get_mock_run_result(diff, threshold, engine, action)
    result_lines = mock_result.splitlines()

    print("=========")
    print("AI generated results:")
    print("Code Execution Test:")
    print(result_lines[0])
    print("\nCode Improvement:")
    print(result_lines[1])
    print("\nUnit Tests:")
    for line in result_lines[2:]:
        print(line)
    print("=========")


def get_git_diff():
    repo = git.Repo('.')
    diff = repo.git.diff()
    return diff


def get_mock_run_result(code, threshold, engine, action=None):
    if action == 'mock_test':
        prompt = f"Please provide a mock test result for the following code changes:\n\n{code}\n\n"
    elif action == 'suggestion':
        prompt = f"Please provide code improvement suggestions for the following code changes:\n\n{code}\n\n"
    elif action == 'unit_test':
        prompt = f"Please generate unit tests for the following code changes:\n\n{code}\n\n"
    else:
        prompt = (
            f"Given the following code changes:\n\n{code}\n\n"
            f"Answer the following questions:\n"
            f"- Can the modified code run correctly? Mock run the code provide what issues may prevent it from running?\n"
            f"- Are the changes an improvement? If not, what suggestions do you have to improve the code?\n"
            f"- Provide example code of unit tests to cover the changes made to the code.\n\n"
            f"Results:\n"
        )

    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=300,
        n=1,
        stop=None,
        temperature=threshold,
    )

    result = response.choices[0].text.strip()
    return result


if __name__ == '__main__':
    main()
