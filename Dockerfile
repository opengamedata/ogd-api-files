# syntax=docker/dockerfile:1
FROM python:3.12-alpine

# Set up environment
ENV PYTHONPATH=src
WORKDIR /usr/src/app

# Copy over necessary files
COPY src/ .
COPY pyproject.toml .
COPY requirements.txt .
COPY config/config.py ./src/config.py

# Run installation of packages
RUN pip install -r requirements.txt
RUN pip install .
RUN pip install waitress

EXPOSE 5000
CMD ["waitress-serve", "app:application"]