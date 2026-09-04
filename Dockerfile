# syntax=docker/dockerfile:1

# STAGE 1: setup dependencies
FROM python:3.12-alpine AS setup

# 1. Set up a venv for easy copying
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN which python
RUN which pip

# 2. Install reqs and the API package into venv
#   Mount, rather than copy, reqs file for installing
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt
COPY src/ogd /app/src/ogd
COPY pyproject.toml /app/pyproject.toml
RUN pip install /app
# 3. Install waitress, for production use
RUN pip install waitress
RUN ls /app/.venv/lib/python3.12/site-packages/

# STAGE 2: Create final image
FROM python:3.12-alpine
WORKDIR /app

# 1. Copy venv from setup stage
COPY --from=setup /app/.venv ./.venv

ENV PATH="/app/.venv/bin:$PATH"
# ENV PYTHONPATH='src'

COPY src/ ./
# Remove redundant copy of the package code
RUN rm -r ./ogd
COPY config/config.py ./config.py
RUN ls /app/.venv/lib/python3.12/site-packages/

CMD ["waitress-serve", "app:application"]