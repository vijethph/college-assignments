FROM python:3.11-slim

WORKDIR /app

COPY Pipfile ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --skip-lock

COPY backend_service/main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
