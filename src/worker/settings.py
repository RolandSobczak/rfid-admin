from shared.settings import BaseSettings
from environs import Env


env = Env()


class Settings(BaseSettings):
    POSTGRES_CONFIG: str
    BACKUP_DIR: str
    DB_NAME: str

    def _load_data(self):
        self.POSTGRES_CONFIG = {
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST"),
            "PORT": env("POSTGRES_PORT", default="5432"),
            "DB": env("POSTGRES_DB"),
        }
        self.BACKUP_DIR = env("BACKUP_DIR", "/var/backup")
        self.DB_NAME = env("DB_NAME")
