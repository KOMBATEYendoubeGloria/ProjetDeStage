from abc import ABC, abstractmethod


class BaseService(ABC):
    """Base class for DevOps service implementations."""

    @abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError
