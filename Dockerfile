FROM python:3.9.6-slim-buster

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]