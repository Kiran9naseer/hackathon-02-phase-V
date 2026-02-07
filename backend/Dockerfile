# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make startup script executable and fix line endings (for Windows)
RUN chmod +x ./startup.sh && \
    sed -i 's/\r$//' ./startup.sh

# Expose the port FastAPI will run on (HF Spaces uses 7860 by default)
EXPOSE 7860

# Command to run the application
ENTRYPOINT ["/bin/bash", "./startup.sh"]
