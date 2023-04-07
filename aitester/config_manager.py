import click

from .config_utils import read_config, store_config


@click.group()
def manage_config():
    """Manage AI Tester configuration."""
    pass


@manage_config.command()
def show():
    """Display the current configuration."""
    config = read_config()
    if config:
        print("Current configuration:")
        for key, value in config.items():
            print(f"{key}: {value}")
    else:
        print("No configuration found.")


@manage_config.command()
@click.argument('language')
def set_language(language):
    """Set Output Language."""
    config = read_config()
    config["language"] = language
    store_config(config)


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
    """Set the GPT engine to use (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4-32k")."""
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


if __name__ == '__main__':
    manage_config()
