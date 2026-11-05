# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.14-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
# tell poetry to now make a virtual env
ENV PYTHONUNBUFFERED=1

# production: debug off. DJANGO_SECRET_KEY comes from the env file on the server
ENV DJANGO_DEBUG=0

# uv from its official image, pinned so builds are repeatable
COPY --from=ghcr.io/astral-sh/uv:0.11.2 /uv /bin/uv
# use this image's Python instead of downloading one, and copy packages into the venv
# rather than linking them to uv's cache
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_LINK_MODE=copy
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY compost_tracker ./compost_tracker
COPY pile_tracker ./pile_tracker
COPY manage.py ./
COPY readme.md ./

# get the database, for debugging
# COPY db.sqlite3 ./

RUN uv sync --locked --no-dev

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--log-level", "debug", "compost_tracker.wsgi"]
# go to this website
# 127.0.0.1:8001/

CMD ["python", "manage.py","runserver", "0.0.0.0:8001"]
