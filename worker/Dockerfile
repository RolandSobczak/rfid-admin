FROM python:3.11.9-bullseye

WORKDIR /src
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget gnupg2 lsb-release && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client-15 && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip3 install poetry


COPY poetry.lock pyproject.toml /src/

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root --no-directory --no-dev

COPY main.py /src/main.py

ENTRYPOINT ["python", "/src/main.py"]


