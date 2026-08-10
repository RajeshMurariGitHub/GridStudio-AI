from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from src.domain.network import Network


class BaseNetworkImporter(ABC):
    """
    Abstract base class for all network importers.
    """

    @abstractmethod
    def load(self, source: str) -> Network:
        """
        Load an electrical network from a source.
        """
        raise NotImplementedError
