#!/usr/bin/env python
import datetime
import os
import sys

BACKUP_PATH = "/var/backup/"

from plumbum.cmd import pg_dump
from plumbum import local
from worker.settings import Settings

settings = Settings()


def backup_db(db_name: str, filename: str):
    with open(filename, mode="w") as f:
        with local.env(PGPASSWORD=settings.POSTGRES_CONFIG["PASSWORD"]):
            (
                pg_dump[
                    "-a",
                    "-Z",
                    "9",
                    "-h",
                    settings.POSTGRES_CONFIG["HOST"],
                    "-U",
                    settings.POSTGRES_CONFIG["USER"],
                    f"--port={settings.POSTGRES_CONFIG['PORT']}",
                    db_name,
                ]
                > f
            )()
            print("BACKUP_CREATED", flush=True)


def main():
    current_time = datetime.datetime.now()
    os.makedirs(BACKUP_PATH + settings.DB_NAME, exist_ok=True)
    backup_db(
        settings.DB_NAME,
        filename=f"{BACKUP_PATH}{settings.DB_NAME}/{current_time.strftime('%Y-%m-%dT%H:%M:%S')}.gz",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
