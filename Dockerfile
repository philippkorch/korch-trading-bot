FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (gcc for some packages)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (force reinstall to bypass cache)
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Cache invalidation - force rebuild (2026-10-05 20:40)
RUN echo "Rebuilt with correct dependencies"

# Run bot
CMD ["python", "korch_trading_bot.py"]
