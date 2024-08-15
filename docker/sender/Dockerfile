FROM python:3.11.9-bullseye

WORKDIR /src
RUN apt-get update && \
    pip3 install poetry

COPY src/sender/poetry.lock src/sender/pyproject.toml /src/

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root --no-directory --no-dev

COPY src/sender/main.py /src/main.py

ENTRYPOINT ["python", "/src/main.py"]


