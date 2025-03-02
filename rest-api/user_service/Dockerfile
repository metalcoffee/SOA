FROM python:3.9-slim

ENV PYTHONPATH="${PYTHONPATH}:/app"
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#  Tests
RUN pip install pytest requests-mock pytest-cov

COPY . .

EXPOSE 5001
CMD ["python", "app.py"]
