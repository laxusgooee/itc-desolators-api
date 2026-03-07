# Use a slim Python image for a smaller footprint
FROM python:3.12-slim

# Install system dependencies needed for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory for the application
# We use /app as the base to match the code's expectation of a parent directory
WORKDIR /app

# Copy dependency files first for better caching
# These are expected in the same directory as the Dockerfile
COPY pyproject.toml uv.lock ./api/

# Install dependencies using uv
# --frozen ensures we use the exact versions from uv.lock
RUN cd api && uv sync --frozen --no-cache --no-dev

# Copy the rest of the application code into the /app/api directory
COPY . ./api/

# Set working directory to the api folder where main.py live
WORKDIR /app/api

# Expose the port the app runs on
EXPOSE 8000

# Set environment variables
# PYTHONPATH ensures the 'app' module can be found
ENV PYTHONPATH="/app/api"
ENV PYTHONUNBUFFERED=1


# Run the application using uvicorn
# We use 'uv run' to ensure the correct virtual environment is used
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
