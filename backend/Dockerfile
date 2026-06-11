FROM python:3.11-slim

# Install Chromium for Puppeteer
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-sandbox \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Set Chromium path for pyppeteer
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PYPPETEER_CHROMIUM_REVISION=0

WORKDIR /app

# Install Python dependencies
COPY requirements-core.txt .
ENV PIP_REQUIRE_HASHES=false
RUN pip install --no-cache-dir --retries 10 --timeout 120 -r requirements-core.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /app/local_storage && chmod 777 /app/local_storage

# Create non-root user for security
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose API port
EXPOSE 8000

# Start Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
