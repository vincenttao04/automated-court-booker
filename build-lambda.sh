#!/usr/bin/env bash
# Build AWS Lambda deployment package (Git Bash)
#
# Windows (Git Bash):
#   ./build-lambda.sh
#
# macOS / Linux:
#   chmod +x build-lambda.sh        # run one-time to make script executable
#   ./build-lambda.sh
#
# Requirements:
#   - Python + pip available on PATH
#   - zip installed
#   - bash (Git Bash, macOS, or Linux)

set -euo pipefail
IFS=$'\n\t'

echo "Cleaning old artifacts..."
rm -rf package lambda.zip

echo "Creating package directory..."
mkdir package

echo "Installing dependencies..."
pip install -r requirements.txt -t package

echo "Copying project files..."
cp -r app package/
cp main.py handler.py config_loader.py config.yaml package/

echo "Removing __pycache__ folders..."
find package -type d -name "__pycache__" -exec rm -rf {} +

echo "Removing bin directory (if exists)..."
rm -rf package/bin

echo "Creating lambda.zip..."
(
  cd package
  zip -r ../lambda.zip .
)

echo "✅ Lambda package built successfully!"
