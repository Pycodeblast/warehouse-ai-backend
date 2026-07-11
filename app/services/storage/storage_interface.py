from abc import ABC, abstractmethod


class StorageInterface(ABC):

    @abstractmethod
    def upload(self, file):
        pass

    @abstractmethod
    def download(self, key):
        pass

    @abstractmethod
    def delete(self, key):
        pass