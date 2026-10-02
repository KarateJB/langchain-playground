# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git

# Delete apt cache to reduce container size
RUN rm -rf /var/lib/apt/lists/*

# Copy the agents project
COPY agents/ /app/

# Install Python dependencies using uv
RUN pip install --no-cache-dir uv && \
    uv sync --system --no-cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command - collect AI news when container starts
CMD ["python", "-m", "agent_langgraph.app", "ainews"]
