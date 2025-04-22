FROM python:3.12-slim AS builder
WORKDIR /app
RUN python -m pip install --no-cache-dir poetry==1.4.2
COPY poetry.lock pyproject.toml .env ./
RUN poetry install --no-root
COPY backend ./backend
EXPOSE 8080
CMD ["poetry", "run", "uvicorn", "backend.src:app", "--host", "0.0.0.0", "--port", "8080"]
