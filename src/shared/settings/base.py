from abc import ABC, abstractmethod
from typing import Dict


class BaseSettings(ABC):
    _args: Dict = {"_is_loaded": False}

    @property
    def is_loaded(self) -> bool:
        return self.is_loaded

    def __init__(self):
        self.__dict__ = self._args

        if not self._args["_is_loaded"]:
            self._load()

    @abstractmethod
    def _load_data(self):
        pass

    def _load(self):
        self._load_data()
        self.__dict__["_is_loaded"] = True
