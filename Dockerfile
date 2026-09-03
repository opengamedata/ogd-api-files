# syntax=docker/dockerfile:1
FROM python:3.12-alpine

ENV PYTHONPATH=src
WORKDIR /usr/src/app
COPY requirements.txt .
COPY src/ .
COPY config/config.py ./src/config.py

RUN pip install -r requirements.txt
RUN pip install .
RUN pip install waitress

EXPOSE 5000
CMD ["waitress-serve", "app:application"]