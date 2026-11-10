FROM python:3.14-slim

# PYTHONDONTWRITEBYTECODE: don't write .pyc files in the container
# PYTHONUNBUFFERED: send output straight to the container log
# UV_PYTHON_DOWNLOADS: use this image's Python instead of downloading one
# UV_LINK_MODE: copy packages into the venv rather than linking to uv's cache
# PATH: run the venv's Python (with Django installed), not the system Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# uv from its official image, pinned so builds are repeatable
COPY --from=ghcr.io/astral-sh/uv:0.11.2 /uv /bin/uv
WORKDIR /app

# Install dependencies before copying the code, so a code change doesn't
# throw away the cached install.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY manage.py ./
COPY compost_tracker ./compost_tracker
COPY pile_tracker ./pile_tracker

# Gather CSS/JS into /app/staticfiles, where WhiteNoise serves them.
RUN python manage.py collectstatic --noinput

# Production: debug off. DJANGO_SECRET_KEY and OPENWEATHER_API_KEY come from
# `docker run --env-file`. The database lives on a volume mounted at /app/db.
ENV DJANGO_DEBUG=0

EXPOSE 8001

# Apply any new migrations to the database, then start gunicorn, a production
# web server (Django's runserver is for development only). Access logs go to
# the container log.
CMD ["sh", "-c", "python manage.py migrate && gunicorn compost_tracker.wsgi --bind 0.0.0.0:8001 --workers 2 --access-logfile -"]
