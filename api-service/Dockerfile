FROM python:3.11-slim

WORKDIR /app

COPY api-service/requirements.txt .
RUN pip install -r requirements.txt

COPY shared/ ./shared/
COPY api-service/main.py .

ENV PYTHONPATH=/app/shared

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]