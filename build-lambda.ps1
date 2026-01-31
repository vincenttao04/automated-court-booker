#!/usr/bin/env pwsh
# Build AWS Lambda deployment package
#
# Windows (Windows PowerShell 5.1):
#   powershell -ExecutionPolicy Bypass -File build-lambda.ps1
#
# Cross-platform (PowerShell 7+, pwsh) - Windows:
#   pwsh build-lambda.ps1
#
# Cross-platform (PowerShell 7+, pwsh) - macOS / Linux:
#   chmod +x build-lambda.ps1       # run one-time to make script executable
#   ./build-lambda.ps1
#
# Requirements:
#   - Python + pip available on PATH
#   - PowerShell 5.1+ (Windows) or PowerShell 7+ (pwsh)

$ErrorActionPreference = "Stop"

Write-Host "Cleaning old artifacts..."
Remove-Item -Recurse -Force package, lambda.zip -ErrorAction SilentlyContinue

Write-Host "Creating package directory..."
New-Item -ItemType Directory -Name package | Out-Null

Write-Host "Installing dependencies..."
pip install -r requirements.txt -t package

Write-Host "Copying project files..."
Copy-Item -Recurse app package/
Copy-Item main.py, handler.py, config_loader.py, config.yaml package/

Write-Host "Removing __pycache__ folders..."
Get-ChildItem package -Recurse -Directory -Filter "__pycache__" |
    Remove-Item -Recurse -Force

Write-Host "Removing bin directory (if exists)..."
Remove-Item -Recurse -Force (Join-Path package "bin") -ErrorAction SilentlyContinue

Write-Host "Creating lambda.zip..."
Compress-Archive -Path (Join-Path package "*") -DestinationPath lambda.zip -Force

Write-Host "✅ Lambda package built successfully!"
