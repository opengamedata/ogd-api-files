# syntax=docker/dockerfile:1
FROM python:3.12-slim-trixie

ENV PYTHONPATH=src
COPY requirements.txt /
COPY src/ /
COPY config/config.py /src/config.py

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]