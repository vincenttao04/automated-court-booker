import os
import yaml
import requests


def load_config():
    """
    Loads configuration data for the app.

    - If CONFIG_URL environment variable exists and is not empty:
        → Fetch config from that remote URL (e.g. from S3 in production).
    - Otherwise:
        → Load local config.yaml file (for development use).
    """

    config_url = os.getenv("CONFIG_URL")

    # Check if CONFIG_URL is set and not empty
    if config_url:
        try:
            print("loading remote config")
            response = requests.get(config_url, timeout=15)
            response.raise_for_status()  # check if the request was successful

            # Convert the yaml content from response.text into a python object
            return yaml.safe_load(response.text)
        except Exception as e:
            raise RuntimeError(f"failed to load remote config from s3/aws: {e}")
    else:
        print("loading local config.yaml")
        with open("config.yaml", "r") as config_file:  # "r" -> read mode
            config_content = yaml.safe_load(config_file)
            return config_content
