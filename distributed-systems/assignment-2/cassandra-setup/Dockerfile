FROM python:3.11-slim

RUN mkdir -p /app
WORKDIR /app

COPY . .

ENV PIPENV_VENV_IN_PROJECT=1

RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

EXPOSE 8000

CMD ["python", "main.py"]