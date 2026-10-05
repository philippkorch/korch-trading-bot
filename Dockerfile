FROM python:3.11-slim

WORKDIR /app

<<<<<<< HEAD
# Установи зависимости системы
=======
# Install system dependencies
>>>>>>> origin/main
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

<<<<<<< HEAD
# Скопируй requirements
COPY requirements.txt .

# Установи Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируй приложение
COPY korch_trading_bot.py .

# Запусти бота
=======
# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Run bot
>>>>>>> origin/main
CMD ["python", "korch_trading_bot.py"]
