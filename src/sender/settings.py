from shared.settings import BaseSettings
from environs import Env

env = Env()


class Settings(BaseSettings):
    RABBIT_CONFIG: dict
    DB_NAME: str

    def _load_data(self):
        self.DB_NAME = env("DB_NAME")

        self.RABBIT_CONFIG = {
            "HOST": env("RABBIT_HOST"),
            "PORT": env("RABBIT_PORT"),
            "USER": env("RABBIT_USER"),
            "PASSWORD": env("RABBIT_PASSWORD"),
        }
