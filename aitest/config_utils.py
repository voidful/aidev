import json
from pathlib import Path


def read_config():
    config_path = Path.home() / ".ai_mock_testing" / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
            return config
    return None


def store_config(config):
    config_path = Path.home() / ".ai_mock_testing" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f)
