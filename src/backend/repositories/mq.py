from typing import List

import pika
import sys
import json
import datetime

from backend.schemas.users import UserCreationModel, TenantProfileSchema
from backend.schemas.tenants import TenantSchema
from backend.schemas.deployments import DeploymentSchema
from .base import BaseService


class MQService(BaseService):
    def __init__(self):
        super().__init__()
        credentials = pika.PlainCredentials(
            self._settings.RABBIT_CONFIG["USER"],
            self._settings.RABBIT_CONFIG["PASSWORD"],
        )
        parameters = pika.ConnectionParameters(
            self._settings.RABBIT_CONFIG["HOST"],
            self._settings.RABBIT_CONFIG["PORT"],
            "/",
            credentials,
        )

        self.connection = pika.BlockingConnection(parameters)

    def __del__(self):
        self.connection.close()

    def request_backup(self, db_name: str):
        channel = self.connection.channel()

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
