# syntax=docker/dockerfile:1
FROM python:3.12-slim-trixie

ENV PYTHONPATH=src
COPY requirements.txt /
COPY src/ /
COPY config/config.py /src/config.py

RUN pip install -r requirements.txt
RUN pip install waitress

EXPOSE 5000
CMD ["waitress-serve", "app:application"]