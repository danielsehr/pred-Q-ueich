FROM python:3.10

WORKDIR /app

# Install libeccodes for cfgrib
RUN apt-get update && apt-get install -y \
    libeccodes0 \
    libeccodes-dev \
    # eccodes \
    && rm -rf /var/lib/apt/lists/*


# Copy uv image, toml and uv lock file
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./


# Sync dependencies only
RUN uv sync --locked --no-install-project


# Copy src code and sync again
COPY src ./src

RUN uv sync --locked


# Define venv 
ENV PATH="/app/.venv/bin:$PATH"


CMD ["python"]