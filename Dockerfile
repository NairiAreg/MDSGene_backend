# Filename: Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Add any other essential system libraries your Python packages might need
# For example, if tabula-py needs Java, you'd install it here.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-jre \
        curl \
        wget \
    && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create necessary directories if they are used by the application and might not exist
# These paths are relative to WORKDIR /app
RUN mkdir -p ./excel ./properties ./temp_uploads ./vector_store/faiss_index ./cache ./.questions ./Model

# Expose ports (these will be mapped in docker-compose.yml)
# Port for main-app
EXPOSE 8000
# Port for AI Processor Service
EXPOSE 8001
# Port for Vector Store Service
EXPOSE 8002

# Default command (can be overridden in docker-compose.yml)
# This is just a placeholder; actual commands will be in docker-compose.
CMD ["python", "main.py"]