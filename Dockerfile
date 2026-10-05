FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (gcc for some packages)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Cache invalidation - v2.1 FINAL: Improved UI, Analysis button fix, Strategy confirmation breakdown, Error handling (2026-10-05 2030)
RUN echo "Build v2.1 with proper error handlers - aiohttp 3.9.0, Analysis/Status handlers fixed"

# Run bot
CMD ["python", "korch_trading_bot.py"]
