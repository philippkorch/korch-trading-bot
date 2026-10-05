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

# Cache invalidation - force rebuild with FULL 8-COMPONENT INTELLECT_city integration (2026-10-05 23:45)
RUN echo "Build v2.1 with ALL 8 INTELLECT_city components: RSI, Stochastic, ROSC, WPR, %R, MACD, MFI, JAP"

# Run bot
CMD ["python", "korch_trading_bot.py"]
