FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Install google-agents-cli as a tool
RUN uv tool install google-agents-cli

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Sync dependencies, including the 'eval' group
RUN uv sync --extra eval

# Copy the rest of the application code
COPY . .

# Default command
CMD ["agents-cli", "eval", "run"]
