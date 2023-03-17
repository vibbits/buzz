FROM python:3.11-slim as python-base

ENV VENV_PATH=/opt/venv

WORKDIR /buzz

COPY . ./
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
      # deps for installing poetry
      curl \
      # deps for building python deps
      build-essential \
    \
    && pip install poetry \
    && python -m venv $VENV_PATH \
    && poetry config virtualenvs.create false \
    \
    # cleanup
    && rm -rf /var/lib/apt/lists/*

RUN poetry install --no-interaction --no-ansi -vvv

FROM python-base as runtime
WORKDIR /buzz
COPY --from=python-base $VENV_PATH $VENV_PATH
COPY . ./