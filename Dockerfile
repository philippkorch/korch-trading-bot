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

# Cache invalidation - force rebuild (2026-10-05 21:00)
RUN echo "Rebuilt with yfinance support and real market data integration"

# Run bot
CMD ["python", "korch_trading_bot.py"]
