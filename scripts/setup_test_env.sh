#!/usr/bin/env bash
# Install system and Python dependencies required for running the test suite.
set -e

# Install system packages needed for OCR tests
sudo apt-get update -y
sudo apt-get install -y tesseract-ocr libtesseract-dev

# Install Python packages
pip install -r requirements.txt -r requirements-test.txt
