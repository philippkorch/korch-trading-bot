FROM python:3.11-slim

WORKDIR /app

# Установи зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Скопируй requirements
COPY requirements.txt .

# Установи Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируй приложение
COPY korch_trading_bot.py .

# Запусти бота
CMD ["python", "korch_trading_bot.py"]
