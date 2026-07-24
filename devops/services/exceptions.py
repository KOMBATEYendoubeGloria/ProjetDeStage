"""Service layer exceptions for provider registry, factory, and DI."""

from .exceptions import DevopsException


class ServiceLayerException(DevopsException):
    """Base exception for service layer failures."""
    pass


class ProviderRegistryError(ServiceLayerException):
    """Raised when provider registry initialization or lookup fails."""
    pass


class ServiceFactoryError(ServiceLayerException):
    """Raised when the factory cannot create an instance."""
    pass


class ServiceContainerError(ServiceLayerException):
    """Raised when the container cannot resolve a dependency."""
    pass
