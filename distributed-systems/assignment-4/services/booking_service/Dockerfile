FROM python:3.11-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --ignore-pipfile

COPY services/booking_service/ ./services/booking_service/
COPY shared/ ./shared/

WORKDIR /app/services/booking_service

ENV PYTHONPATH=/app
ENV SERVICE_PORT=8000
ENV HOTEL_SERVICE_URL=http://hotel-service:8000
ENV USER_SERVICE_URL=http://user-service:8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
