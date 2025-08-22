FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Dependências de sistema para o WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libjpeg-dev \
    libxml2 \
    libgdk-pixbuf-xlib-2.0-dev \
    libxslt1-dev \
    libssl-dev \
    libglib2.0-0 \
    fonts-liberation \
    fonts-dejavu \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
