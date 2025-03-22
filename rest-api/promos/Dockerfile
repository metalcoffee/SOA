FROM python:3.9-slim

WORKDIR /app

RUN mkdir -p /app/data && chmod 777 /app/data

COPY service/requirements.txt .
RUN pip install -r requirements.txt

COPY service/ ./service/
COPY proto/ ./proto/

ENV PYTHONPATH="${PYTHONPATH}:/app:/app/service"

EXPOSE 5003
CMD ["python", "-u", "/app/service/promo_service.py"]