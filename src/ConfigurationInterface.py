"""
this is the abstract class to create the blueprint for the
interaction between the UI and the configuration database
"""

from abc import ABC, abstractmethod

class ConfigInterface(ABC):
    def __init__(self):
        pass

    # create the hidden directory
    def setup_hidden_directory(self):
        pass

    # create the configuration db
    def setup_configuration_database(self):
        pass

    @abstractmethod
    def get_default_directory(self) -> str:
        pass

    @abstractmethod
    def update_default_directory(self, new_directory: str) -> None:
        pass