# Standard Library
import os

# Third-Party Libraries
import boto3
import yaml


def load_config():
    """
    Loads configuration data for the app.

    - If S3_BUCKET and S3_KEY environment variables exist:
        → Fetch config from S3 using boto3 (authenticated via IAM role).
    - Otherwise:
        → Load local config.yaml file (for development use).
    """

    s3_bucket = os.getenv("S3_BUCKET")
    s3_key = os.getenv("S3_KEY")

    # Check if CONFIG_URL is set and not empty
    if s3_bucket and s3_key:
        try:
            print(
                "loading config from s3/aws"
            )  # debug log - can delete after s3 implemented

            s3 = boto3.client("s3")
            response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
            content = response["Body"].read().decode("utf-8")

            return yaml.safe_load(content)
        except Exception as error:
            raise RuntimeError(f"failed to load config from s3/aws: {error}")
    else:
        # print("loading local config.yaml") # debug log - can delete after s3 implemented
        with open("config.yaml", "r") as config_file:  # "r" -> read mode
            print(
                "loading config from local file"
            )  # debug log - can delete after s3 implemented

            return yaml.safe_load(config_file)
