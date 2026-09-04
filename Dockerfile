# syntax=docker/dockerfile:1

# STAGE 1: setup dependencies
FROM python:3.12-alpine AS setup

# 1. Set up a venv for easy copying
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN which python
RUN which pip

# 2. Install reqs into venv
#   Mount, rather than copy, reqs file for installing
RUN --mount=type=bind,source=requirements-build.txt,target=requirements-build.txt \
    pip install -r requirements-build.txt
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt
RUN --mount=type=bind,source=requirements-production.txt,target=requirements-production.txt \
    pip install -r requirements-production.txt
COPY src/ogd /app/src/ogd
COPY pyproject.toml /app/pyproject.toml
# 3. Install local copy of API package code.
RUN pip install /app
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

CMD ["gunicorn", \
     "--bind",    ":8080", \
     "--workers", "1", "\
     --threads",  "8", \
     "--timeout", "0", \
     "app:application" \
]