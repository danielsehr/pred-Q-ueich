FROM python:3.10

WORKDIR /app

COPY pyproject.toml .

COPY src/ src/

RUN pip install -e .

ENV PYTHONUNBUFFERED=1