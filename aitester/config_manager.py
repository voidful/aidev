import click

from .config_utils import read_config, store_config


@click.group()
@click.option('--set-api-key', help='Set the OpenAI API key.')
@click.option('--set-threshold', type=float,
              help='Set the confidence threshold for the AI generated result (0.0 to 1.0).')
@click.option('--set-engine', help='Set the GPT-3 engine to use (e.g., "text-davinci-002", "text-curie-002").')
@click.option('--set-max-tokens', type=int, help='Set the maximum number of tokens in the AI-generated response.')
@click.option('--set-suggestions-only', type=bool,
              help='Set whether to display only code improvement suggestions (True or False).')
def manage_config(set_api_key, set_threshold, set_engine, set_max_tokens, set_suggestions_only):
    config = read_config() or {}

    if set_api_key:
        config['api_key'] = set_api_key
    if set_threshold:
        config['threshold'] = set_threshold
    if set_engine:
        config['engine'] = set_engine
    if set_max_tokens:
        config['max_tokens'] = set_max_tokens
    if set_suggestions_only is not None:
        config['suggestions_only'] = set_suggestions_only

    store_config(config)
    print("Configuration updated successfully.")


@manage_config.command()
@click.argument('api_key')
def set_api_key(api_key):
    """Set the OpenAI API key."""
    config = read_config() or {}
    config['api_key'] = api_key
    store_config(config)
    print("API key updated successfully.")


@manage_config.command()
@click.argument('threshold', type=float)
def set_threshold(threshold):
    """Set the confidence threshold for the AI generated result (0.0 to 1.0)."""
    config = read_config() or {}
    config['threshold'] = threshold
    store_config(config)
    print("Threshold updated successfully.")


@manage_config.command()
@click.argument('engine')
def set_engine(engine):
    """Set the GPT-3 engine to use (e.g., "text-davinci-002", "text-curie-002")."""
    config = read_config() or {}
    config['engine'] = engine
    store_config(config)
    print("Engine updated successfully.")


@manage_config.command()
@click.argument('max_tokens', type=int)
def set_max_tokens(max_tokens):
    """Set the maximum number of tokens in the AI-generated response."""
    config = read_config() or {}
    config['max_tokens'] = max_tokens
    store_config(config)
    print("Max tokens updated successfully.")


@manage_config.command()
@click.argument('suggestions_only', type=bool)
def set_suggestions_only(suggestions_only):
    """Set whether to display only code improvement suggestions (True or False)."""
    config = read_config() or {}
    config['suggestions_only'] = suggestions_only
    store_config(config)
    print("Suggestions only setting updated successfully.")


if __name__ == '__main__':
    manage_config()
