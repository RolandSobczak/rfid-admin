FROM python:3.11.8 as lint

WORKDIR /src

COPY src/shared /src/shared
COPY src/backend /src/backend

RUN pip3 install black isort && \
  python -m black /src && \
  python -m isort /src


FROM python:3.11.8 as deps

WORKDIR /tmp

ARG POETRY_CACHE_DIR=/usr/local/lib/python3.12/site-packages/

COPY src/backend/poetry.lock src/backend/pyproject.toml /tmp/

RUN pip3 install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-root --no-directory --no-dev


FROM python:3.11.8 as run

WORKDIR /src

ARG BUILD_ENV=prod
ARG BUILD_USER=python
ARG POETRY_CACHE_DIR=/usr/local/lib/python3.11/site-packages/

RUN addgroup --system python && \
  adduser --system --home /home/python --ingroup python python

COPY --from=deps --chown=python:python /tmp /src
COPY --from=deps --chown=python:python /usr/local/bin /usr/local/bin
COPY --from=deps --chown=python:python /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev && \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
  rm -rf /var/lib/apt/lists/*

RUN if [ ${BUILD_ENV} = "dev" ]; then \
  pip3 install poetry && \
  python -m poetry config virtualenvs.create false && \
  python -m poetry install --no-interaction --no-root; \
  else \
  rm -f /src/poetry.lock /src/pyproject.toml; \
  fi

COPY --chown=python:python src/backend/poetry.lock /src/backend/pyproject.toml /src/
COPY  --chown=python:python src/shared /src/shared
COPY --from=lint --chown=python:python src/backend /src/backend
COPY docker/backend/entrypoint.sh /entrypoint.sh
RUN chmod 777 /entrypoint.sh
COPY docker/backend/callback.py /callback.py
RUN chmod 777 /callback.py

ENV TZ Europe/Warsaw

USER ${BUILD_USER}

ENV PROJECT_PATH /src/
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH=${PYTHONPATH}:/src/
ENV PATH=/usr/local/bin/python:/usr/local/bin:${PATH}

CMD ["/entrypoint.sh"]

