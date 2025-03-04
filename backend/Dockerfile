FROM python:3.12-slim AS builder
WORKDIR /opt/app/
RUN python -m pip install --no-cache-dir poetry==1.4.2
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root
COPY . .