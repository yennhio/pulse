FROM python:3.11-slim

WORKDIR /app

COPY worker-service/requirements.txt .
RUN pip install -r requirements.txt

COPY shared/ ./shared/
COPY worker-service/main.py .

ENV PYTHONPATH=/app/shared

CMD ["python", "-u", "main.py"]