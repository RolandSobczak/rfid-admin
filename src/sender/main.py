#!/usr/bin/env python
import datetime
import json
import os


import pika


def request_backup(db_name: str):
    credentials = pika.PlainCredentials("rfid", "vK177~g)(22@")
    parameters = pika.ConnectionParameters("192.168.0.92", 31118, "/", credentials)

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
    request_backup(os.environ["DB_NAME"])


if __name__ == "__main__":
    main()
