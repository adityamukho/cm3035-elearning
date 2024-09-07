#!/usr/bin/env bash
# Exit on error
set -o errexit

export DEBUG=True
# export OPENAI_API_KEY=sk-proj-insert-your-key-here-for-chat-moderation

python -m gunicorn elearning.asgi:application -k uvicorn.workers.UvicornWorker