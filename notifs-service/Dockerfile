FROM python:3.11-slim

WORKDIR /app

COPY notifs-service/requirements.txt .
RUN pip install -r requirements.txt

COPY notifs-service/main.py .

ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]