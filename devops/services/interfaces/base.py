from abc import ABC
from typing import Any


class ServiceInterface(ABC):
    """Base interface for all DevOps service contracts.

    Responsibilities:
        - Define a common abstraction for service operations.
        - Prevent domain code from depending on concrete implementations.
    """

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute a generic service operation."""
        raise NotImplementedError
