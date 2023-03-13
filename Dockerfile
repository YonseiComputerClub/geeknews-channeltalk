FROM python:alpine

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app
ENTRYPOINT [ "uvicorn", "main:app" ]