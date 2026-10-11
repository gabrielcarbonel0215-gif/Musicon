FROM python:3.11-slim

# Install system dependencies (ffmpeg and curl)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (default 7860 for Hugging Face Spaces or 8000)
ENV PORT=7860
EXPOSE 7860

CMD ["python", "server.py"]
