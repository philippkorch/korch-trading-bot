FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for matplotlib, PIL, and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy v4.0 requirements
COPY requirements_v4.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_v4.txt

# Copy bot files
COPY . .

# Build cache invalidation - v4.0: Minimalist Interface, Real-time Analysis, Charts Support
RUN echo "Build v4.0 - Minimalist Interface with Charts Support (2026-10-10)"

# Run bot with charts support
CMD ["python", "korch_bot_v4_with_charts.py"]
