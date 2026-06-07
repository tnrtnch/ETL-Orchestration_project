FROM python:3.11-slim

# Working directory
WORKDIR /app

# System dependencies (required for Scrapy)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the codes
COPY . .

# Default run command
CMD ["scrapy", "crawl", "eu_spider"]
