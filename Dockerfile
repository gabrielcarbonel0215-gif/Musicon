FROM python:3.11-slim

# Install system dependencies (ffmpeg, curl, Node.js 20 LTS and Deno for yt-dlp JS runtime)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl gnupg unzip && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    curl -fsSL https://deno.land/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.deno/bin:$PATH"

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
