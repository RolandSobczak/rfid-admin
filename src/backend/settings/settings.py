from shared.settings import BaseSettings
from environs import Env

env = Env()


class Settings(BaseSettings):
    AUTH_API_HOST: str
    TENANT_API_TEMPLATE: str
    DBHOST: str
    NAMESPACE = "rfid-main"
    INSIDE_CLUSTER: bool
    RABBIT_CONFIG: dict
    POSTGRES_CONFIG: dict

    def _load_data(self):
        env.read_env("../../env/backend.env")

        self.AUTH_API_HOST = env("AUTH_API_HOST")
        self.PUBLIC_KEY = env("PUBLIC_KEY")
        self.TENANT_API_TEMPLATE = env("TENANT_API_TEMPLATE")

        self.POSTGRES_HOST = env("POSTGRES_HOST")
        self.POSTGRES_PORT = env("POSTGRES_PORT")
        self.POSTGRES_USER = env("POSTGRES_USER")
        self.POSTGRES_PASSWORD = env("POSTGRES_PASSWORD")

        self.DBHOST = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
        self.NAMESPACE = env("NAMESPACE")
        self.INSIDE_CLUSTER = env.bool("INSIDE_CLUSTER")
        self.RABBIT_CONFIG = {
            "HOST": env("RABBIT_HOST"),
            "PORT": env.int("RABBIT_PORT"),
            "USER": env("RABBIT_USER"),
            "PASSWORD": env("RABBIT_PASSWORD"),
        }
        self.CORS_CONFIG = {
            "ALLOWED_ORIGINS": env.list("ALLOWED_ORIGINS"),
            "ALLOW_CREDENTIALS": env.bool("ALLOW_CREDENTIALS"),
            "ALLOWED_METHODS": env.list("ALLOWED_METHODS"),
            "ALLOWED_HEADERS": env.list("ALLOWED_HEADERS"),
        }
