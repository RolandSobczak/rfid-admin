#!/usr/bin/env python
import datetime
import json

import pika

from sender.settings import Settings


settings = Settings()


def request_backup(db_name: str):
    credentials = pika.PlainCredentials(
        settings.RABBIT_CONFIG["USER"], settings.RABBIT_CONFIG["PASSWORD"]
    )
    parameters = pika.ConnectionParameters(
        settings.RABBIT_CONFIG["HOST"], settings.RABBIT_CONFIG["PORT"], "/", credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange="backups", exchange_type="topic")
    channel.basic_qos(prefetch_count=1)

    routing_key = "admin.backups"
    msg = json.dumps(
        {
            "db_name": db_name,
            "created_at": str(datetime.datetime.now()),
        }
    )
    channel.basic_publish(exchange="backups", routing_key=routing_key, body=msg)


def main():
    request_backup(settings.RABBIT_CONFIG["DB_NAME"])


if __name__ == "__main__":
    main()
