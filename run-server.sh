#!/usr/bin/env bash

set -e

source .venv/bin/activate
lsof -ti :8000 | xargs -r kill -9
exec gunicorn main:app --config config.py --reload
