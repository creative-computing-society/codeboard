FROM python:3.13-slim

# Prevent .pyc files + enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system deps (build tools, curl, psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl build-essential gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Configure Poetry (no virtualenvs inside the container — correct for Docker)
RUN poetry config virtualenvs.in-project false
RUN poetry config virtualenvs.create false

# Copy only the poetry files first (trying poetry out + good caching)
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY . /app

# Gunicorn + Uvicorn workers for ASGI Django
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-w", "6", "--timeout=300"]
