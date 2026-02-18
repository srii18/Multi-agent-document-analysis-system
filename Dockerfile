# Stage 1: Python application
FROM python:3.11-slim as app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
# 8000 for MCP Server
# 11434 for Ollama (if running in same container, which we won't do)
EXPOSE 8000

# Default to MCP server; can be overridden
CMD ["python", "mcp_server/server.py"]
