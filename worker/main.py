#!/usr/bin/env python
import datetime
import json
import os

import gzip

import pika

BACKUP_PATH = "/var/backup/"

from plumbum.cmd import pg_dump
from plumbum import local


def backup_db(db_name: str, filename: str):
    with open(filename, mode="w") as f:
        with local.env(PGPASSWORD="n1S8&e3H&,m&"):
            (
                pg_dump[
                    "-a",
                    "-Z",
                    "9",
                    "-h",
                    "192.168.0.92",
                    "-U",
                    "rfid",
                    "--port=31118",
                    db_name,
                ]
                > f
            )()


def callback(ch, method, properties, body):
    if "backups" in method.routing_key:
        req = json.loads(body)
        os.makedirs(BACKUP_PATH + req["db_name"], exist_ok=True)
        backup_db(
            req["db_name"],
            filename=f"{BACKUP_PATH}{req['db_name']}/{str(req['created_at'])}.gz",
        )


def main():
    credentials = pika.PlainCredentials("rfid", "vK177~g)(22@")
    parameters = pika.ConnectionParameters("192.168.0.92", 31118, "/", credentials)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    channel.exchange_declare(exchange="backups", exchange_type="topic")

    result = channel.queue_declare("backups", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange="backups", queue=queue_name, routing_key="admin.*")

    print(" [*] Waiting for logs. To exit press CTRL+C")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    # backup_db("auth")
