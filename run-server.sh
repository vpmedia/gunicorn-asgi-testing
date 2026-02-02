#!/usr/bin/env bash

set -e

source .venv/bin/activate
exec gunicorn main:app --config config.py --reload
