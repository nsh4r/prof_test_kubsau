FROM python:3.12-slim AS builder
WORKDIR /opt/app/
RUN python -m pip install --no-cache-dir poetry==1.4.2
COPY . .
RUN poetry install --no-root
EXPOSE 8080
CMD ["poetry", "run", "uvicorn", "backend.src:app", "--host", "0.0.0.0", "--port", "8080"]