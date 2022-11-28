FROM python:3.9.6-slim-buster

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get install -yq netcat \
    && pip install psycopg2

COPY requirements.txt .

RUN pip install -r requirements.txt 

COPY ./docker/postgres/init-postgres.sql /docker-entrypoint-initdb.d/

RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres"]

COPY . .

ENTRYPOINT ["sh", "./db_scripts/start.sh"]