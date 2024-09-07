#!/usr/bin/env bash
# Exit on error
set -o errexit

export DEBUG=True

# export EMAIL_HOST=your_email_host
# export EMAIL_HOST_PASSWORD=your_email_host_password
# export EMAIL_HOST_USER=your_email_host_user
# export EMAIL_PORT=your_email_port

celery -A elearning.celery worker --loglevel=info
