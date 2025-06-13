FROM python:3.9-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m appuser

# Base stage for common setup
FROM base as common
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R appuser:appuser /app

# Stage for database initialization
FROM common as db-init
USER appuser
CMD ["python", "utils/sql_executor.py"]

# Stage for main application
FROM common as app
USER appuser
CMD ["python", "main.py"] 