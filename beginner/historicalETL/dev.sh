#!/bin/bash
cd "$(dirname "$0")"
nodemon --exec "uv run python main.py" --ext py