# Python ka stable version use karein
FROM python:3.10-slim

# Working directory set karein
WORKDIR /app

# System dependencies (agar zaroorat ho)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Requirements copy karke install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saara code copy karein
COPY . .

# Bot ko run karne ki command
CMD ["python", "main.py"]

