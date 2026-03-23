FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=.
# Change 'your-username/model-name' to your actual HF Model Hub ID
ENV MODEL_PATH=your-username/subtext-intent-baseline

# Expose port 7860 (Default for Hugging Face Spaces)
EXPOSE 7860

# Run the application
# We use --host 0.0.0.0 to bind to all interfaces for container access
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
