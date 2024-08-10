from src.settings import get_settings


class BaseService:
    def __init__(self):
        self._settings = get_settings()
