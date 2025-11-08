import os
import yaml
import requests

def load_config():
    """
    Loads the booking configuration.
    - If CONFIG_URL environment variable exists, fetch config from remote URL (S3 in production)
    - Otherwise, load local config.yaml for development.
    """
    config_url = os.getenv("CONFIG_URL")

    if config_url:
        try:
            print(f"Loading remote config from {config_url}...")
            response = requests.get(config_url)
            response.raise_for_status()
            return yaml.safe_load(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to load remote config from {config_url}: {e}")
    else:
        print("Loading local config.yaml...")
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
