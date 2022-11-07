FROM python:3.9.6-slim-buster

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install -r requirements.txt \
    && apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

COPY . .

ENTRYPOINT ["gunicorn", "--workers=2", "main:app", "--bind", "0.0.0.0:8000", "--reload"]
