from shared.settings import BaseSettings
from environs import Env


env = Env()


class Settings(BaseSettings):
    POSTGRES_CONFIG: str
    RABBIT_CONFIG: str
    BACKUP_DIR: str

    def _load_data(self):
        self.POSTGRES_CONFIG = {
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST"),
            "PORT": env("POSTGRES_PORT", default="5432"),
            "DB": env("POSTGRES_DB"),
        }
        self.RABBIT_CONFIG = {
            "HOST": env("RABBIT_HOST"),
            "PORT": env("RABBIT_PORT"),
            "USER": env("RABBIT_USER"),
            "PASSWORD": env("RABBIT_PASSWORD"),
        }
        self.BACKUP_DIR = env("BACKUP_DIR", "/var/backup")
