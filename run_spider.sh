#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "Virtual environment not found at ./venv"
  echo "Create it with: python3 -m venv venv"
  exit 1
fi

source venv/bin/activate
python -m scrapy "$@"
