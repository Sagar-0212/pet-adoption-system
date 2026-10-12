# Use official lightweight Python 3.9 base image
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files to disc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Layer Caching Optimization: copy requirements and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, static frontend, and project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Launch Uvicorn server bound to all interfaces
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
