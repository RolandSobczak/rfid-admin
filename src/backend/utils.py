import itertools
import os
from collections.abc import Mapping, Sequence
from copy import copy

import sqlalchemy as sa
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy_utils.functions.orm import quote


def _set_url_database(url: sa.engine.url.URL, database):
    """Set the database of an engine URL.

    :param url: A SQLAlchemy engine URL.
    :param database: New database to set.

    """
    if hasattr(url, "_replace"):
        # Cannot use URL.set() as database may need to be set to None.
        ret = url._replace(database=database)
    else:  # SQLAlchemy <1.4
        url = copy(url)
        url.database = database
        ret = url
    assert ret.database == database, ret
    return ret


def _get_scalar_result(engine, sql):
    with engine.connect() as conn:
        return conn.scalar(sql)


def database_exists(url, **connection_args):
    """This function is basically a copy of the one from sqlalchemy_utils lib.
    The reason to just copy and paste this code is that,
    standard version doesn't provide any timeout for the sa connection.
    """

    url = make_url(url)
    database = url.database
    engine = None
    try:
        text = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
        for db in (database, "postgres", "template1", "template0", None):
            url = _set_url_database(url, database=db)
            engine = sa.create_engine(url, connect_args=connection_args)
            try:
                return bool(_get_scalar_result(engine, sa.text(text)))
            except (ProgrammingError, OperationalError):
                pass
        return False
    finally:
        if engine:
            engine.dispose()


def create_database(url, encoding="utf8", template=None, **connection_args):
    """This function is basically a copy of the one from sqlalchemy_utils lib.
    The reason to just copy and paste this code is that,
    standard version doesn't provide any timeout for the sa connection.
    """

    url = make_url(url)
    database = url.database
    dialect_driver = url.get_dialect().driver
    url = _set_url_database(url, database="postgres")

    if dialect_driver in {
        "asyncpg",
        "pg8000",
        "psycopg",
        "psycopg2",
        "psycopg2cffi",
    }:
        engine = sa.create_engine(
            url, isolation_level="AUTOCOMMIT", connect_args=connection_args
        )
    else:
        engine = sa.create_engine(url, connect_args=connection_args)

    if not template:
        template = "template1"

    with engine.begin() as conn:
        text = "CREATE DATABASE {} ENCODING '{}' TEMPLATE {}".format(
            quote(conn, database), encoding, quote(conn, template)
        )
        conn.execute(sa.text(text))

    engine.dispose()


def drop_database(url, **connection_args):
    """Issue the appropriate DROP DATABASE statement.

    :param url: A SQLAlchemy engine URL.

    Works similar to the :func:`create_database` method in that both url text
    and a constructed url are accepted.

    ::

        drop_database('postgresql://postgres@localhost/name')
        drop_database(engine.url)

    """

    url = make_url(url)
    database = url.database
    url = _set_url_database(url, database="postgres")
    engine = sa.create_engine(
        url, isolation_level="AUTOCOMMIT", connect_args=connection_args
    )
    with engine.begin() as conn:
        version = conn.dialect.server_version_info
        pid_column = "pid" if (version >= (9, 2)) else "procpid"
        text = """
        SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{database}'
        AND {pid_column} <> pg_backend_pid();
        """.format(
            pid_column=pid_column, database=database
        )
        conn.execute(sa.text(text))

        text = f"DROP DATABASE {quote(conn, database)}"
        conn.execute(sa.text(text))

    engine.dispose()
