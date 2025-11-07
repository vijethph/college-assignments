FROM python:3.11-slim

WORKDIR /app

COPY Pipfile ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --skip-lock

COPY client_service/main.py .

EXPOSE 9090

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9090"]
