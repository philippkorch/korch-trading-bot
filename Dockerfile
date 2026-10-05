FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (gcc for some packages)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (force reinstall to bypass cache)
# Using explicit requirement override to ensure correct aiohttp version
RUN pip install --no-cache-dir \
    python-telegram-bot==20.3 \
    requests==2.31.0 \
    numpy==1.26.0 \
    python-dateutil==2.8.2 \
    aiohttp==3.9.0 \
    matplotlib==3.8.0 \
    Pillow==10.0.0

# Copy bot files
COPY . .

# Cache invalidation - force rebuild (2026-10-05 17:41)
RUN echo "Rebuilt with correct dependencies and aiohttp==3.9.0"

# Run bot
CMD ["python", "korch_trading_bot.py"]
