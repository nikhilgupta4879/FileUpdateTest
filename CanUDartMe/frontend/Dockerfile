FROM python:3.12-slim

WORKDIR /app

# Install Flet system deps for Linux web server mode
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Serve as web app on port 8080
CMD ["flet", "run", "--web", "--port", "8080", "app/main.py"]
