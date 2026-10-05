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

# Cache invalidation - v2.1 FINAL: Improved UI, Analysis button fix, Strategy confirmation breakdown (2026-10-05 2100)
RUN echo "Build v2.1-FINAL with: Analysis button timeout handling, Status/Demo signals with strategy breakdown, All 8 INTELLECT components"

# Run bot
CMD ["python", "korch_trading_bot.py"]
