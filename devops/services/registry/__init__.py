"""Provider registry and discovery for DevOps service implementations."""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from typing import Any, Dict, Iterable, List, Optional, Type

from ..interfaces.base import ServiceInterface
from ...exceptions import DevopsException
from ..providers.service_provider import ServiceProvider

logger = logging.getLogger(__name__)


class ProviderRegistryException(DevopsException):
    """Base exception raised by the provider registry."""


class ProviderNotFoundException(ProviderRegistryException):
    """Raised when no matching provider is registered."""


class ProviderRegistrationException(ProviderRegistryException):
    """Raised when a provider cannot be registered."""


class ProviderCompatibilityException(ProviderRegistryException):
    """Raised when a provider is incompatible."""


class ProviderRegistry:
    """Registry for provider implementations keyed by interface and provider name."""

    _registry: Dict[Type[ServiceInterface], Dict[str, ServiceProvider]] = {}
    _defaults: Dict[Type[ServiceInterface], str] = {}
    _initialized: bool = False

    @classmethod
    def register(
        cls,
        interface: Type[ServiceInterface],
        provider_name: str,
        implementation: Type[ServiceInterface],
        config: Optional[Dict[str, Any]] = None,
        active: bool = True,
    ) -> None:
        provider_name = cls._normalize_provider_name(provider_name)
        if not inspect.isclass(implementation):
            raise ProviderRegistrationException('Implementation must be a class')
        if not issubclass(implementation, interface):
            raise ProviderRegistrationException(
                f'{implementation.__name__} does not implement {interface.__name__}'
            )
        if inspect.isabstract(implementation):
            raise ProviderRegistrationException(
                f'Cannot register abstract implementation {implementation.__name__}'
            )

        metadata = cls._build_metadata(interface, provider_name, implementation, config, active)
        cls._validate_provider(metadata)

        providers = cls._registry.setdefault(interface, {})
        providers[provider_name] = metadata
        logger.info('Registered provider %s for interface %s', provider_name, interface.__name__)

    @classmethod
    def get(cls, interface: Type[ServiceInterface], provider_name: Optional[str] = None) -> Type[ServiceInterface]:
        return cls.get_provider(interface, provider_name).implementation

    @classmethod
    def get_provider(
        cls,
        interface: Type[ServiceInterface],
        provider_name: Optional[str] = None,
        active_only: bool = True,
    ) -> ServiceProvider:
        cls._ensure_initialized()
        providers = cls._registry.get(interface, {})
        if active_only:
            providers = {name: provider for name, provider in providers.items() if provider.active}

        if not providers:
            state = 'active ' if active_only else ''
            raise ProviderNotFoundException(
                f'No {state}providers registered for interface {interface.__name__}'
            )

        if provider_name is None:
            provider_name = cls._defaults.get(interface) or cls._default_provider_name(providers)

        provider_name = cls._normalize_provider_name(provider_name)

        provider = providers.get(provider_name)
        if provider is None:
            raise ProviderNotFoundException(
                f'Provider {provider_name} not registered for interface {interface.__name__}. '
                f'Available providers: {list(providers.keys())}'
            )
        if active_only and not provider.active:
            raise ProviderNotFoundException(
                f'Provider {provider_name} for interface {interface.__name__} is inactive.'
            )

        return provider

    @classmethod
    def available_providers(cls, interface: Type[ServiceInterface], active_only: bool = True) -> List[str]:
        cls._ensure_initialized()
        providers = cls._registry.get(interface, {})
        if active_only:
            providers = {name: provider for name, provider in providers.items() if provider.active}
        return sorted(providers.keys())

    @classmethod
    def available_service_providers(cls, interface: Type[ServiceInterface], active_only: bool = True) -> List[ServiceProvider]:
        cls._ensure_initialized()
        providers = cls._registry.get(interface, {})
        if active_only:
            providers = [provider for provider in providers.values() if provider.active]
        else:
            providers = list(providers.values())
        return providers

    @classmethod
    def activate(cls, interface: Type[ServiceInterface], provider_name: str) -> None:
        provider = cls.get_provider(interface, provider_name, active_only=False)
        provider.active = True
        provider.status = 'active'
        logger.info('Activated provider %s for interface %s', provider_name, interface.__name__)

    @classmethod
    def deactivate(cls, interface: Type[ServiceInterface], provider_name: str) -> None:
        provider = cls.get_provider(interface, provider_name, active_only=False)
        provider.active = False
        provider.status = 'inactive'
        logger.info('Deactivated provider %s for interface %s', provider_name, interface.__name__)
        cls._assert_active_provider(interface)

    @classmethod
    def set_default_provider(cls, interface: Type[ServiceInterface], provider_name: str) -> None:
        provider = cls.get_provider(interface, provider_name, active_only=False)
        if not provider.active:
            raise ProviderRegistrationException(
                f'Cannot set inactive provider {provider_name} as default for interface {interface.__name__}'
            )
        cls._defaults[interface] = provider_name
        logger.info('Set default provider %s for interface %s', provider_name, interface.__name__)

    @classmethod
    def get_default_provider(cls, interface: Type[ServiceInterface]) -> ServiceProvider:
        return cls.get_provider(interface, None)

    @classmethod
    def refresh(cls, package_names: Optional[List[str]] = None) -> None:
        """Reload provider metadata and refresh registry state."""
        cls._registry.clear()
        cls._initialized = False
        cls._defaults.clear()
        cls._scan_and_register(package_names)
        cls._initialized = True
        logger.info('Provider registry refreshed')

    @classmethod
    def get_container_provider(cls, provider_name: Optional[str] = None) -> Type[ServiceInterface]:
        from ..interfaces.container import ContainerInterface
        return cls.get(ContainerInterface, provider_name)

    @classmethod
    def get_git_provider(cls, provider_name: Optional[str] = None) -> Type[ServiceInterface]:
        from ..interfaces.git import GitInterface
        return cls.get(GitInterface, provider_name)

    @classmethod
    def get_hypervisor_provider(cls, provider_name: Optional[str] = None) -> Type[ServiceInterface]:
        from ..interfaces.hypervisor import HypervisorInterface
        return cls.get(HypervisorInterface, provider_name)

    @classmethod
    def _default_provider_name(cls, providers: Dict[str, ServiceProvider]) -> str:
        if 'default' in providers:
            return 'default'
        if len(providers) == 1:
            return next(iter(providers))
        raise ProviderNotFoundException(
            'Multiple providers are registered; explicit provider_name is required.'
        )

    @classmethod
    def _normalize_provider_name(cls, provider_name: str) -> str:
        return provider_name.strip().lower()

    @classmethod
    def _ensure_initialized(cls) -> None:
        if cls._initialized:
            return
        cls._scan_and_register(None)
        cls._initialized = True

    @classmethod
    def _scan_and_register(cls, package_names: Optional[List[str]] = None) -> None:
        if package_names is None:
            package_names = ['devops.services.implementations']

        for package_name in package_names:
            try:
                implementations_pkg = importlib.import_module(package_name)
            except Exception as exc:
                logger.error('Unable to import provider package %s: %s', package_name, exc)
                continue

            for finder, module_name, _ in pkgutil.walk_packages(implementations_pkg.__path__, implementations_pkg.__name__ + '.'):
                try:
                    module = importlib.import_module(module_name)
                except Exception as exc:
                    logger.warning('Skipping provider module %s because it failed to import: %s', module_name, exc)
                    continue

                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if not inspect.isclass(attribute):
                        continue
                    if attribute is ServiceInterface or inspect.isabstract(attribute):
                        continue
                    if not issubclass(attribute, ServiceInterface):
                        continue
                    provider_name = getattr(attribute, 'provider_name', None)
                    if not provider_name:
                        continue
                    interface = cls._find_service_interface(attribute)
                    if interface is None:
                        logger.warning('Unable to infer interface for provider %s', attribute.__name__)
                        continue
                    try:
                        cls.register(interface, provider_name, attribute)
                    except ProviderRegistryException as exc:
                        logger.warning('Skipping invalid provider %s: %s', attribute.__name__, exc)

    @classmethod
    def _build_metadata(
        cls,
        interface: Type[ServiceInterface],
        provider_name: str,
        implementation: Type[ServiceInterface],
        config: Optional[Dict[str, Any]],
        active: bool,
    ) -> ServiceProvider:
        provider = ServiceProvider(
            interface=interface,
            provider_name=provider_name,
            implementation=implementation,
            module=implementation.__module__,
            version=getattr(implementation, 'provider_version', '0.0.0'),
            description=getattr(implementation, 'provider_description', ''),
            author=getattr(implementation, 'provider_author', ''),
            capabilities=list(getattr(implementation, 'provider_capabilities', [])) or [provider_name],
            compatibility=getattr(implementation, 'provider_compatibility', None),
            dependencies=list(getattr(implementation, 'provider_dependencies', [])),
            config=config or {},
            active=active,
        )
        return provider

    @classmethod
    def _validate_provider(cls, provider: ServiceProvider) -> None:
        cls._assert_interface_compatibility(provider)
        cls._assert_instantiable(provider)
        cls._assert_dependencies(provider)
        cls._assert_project_compatibility(provider)

    @classmethod
    def _assert_interface_compatibility(cls, provider: ServiceProvider) -> None:
        implementation = provider.implementation
        interface = provider.interface
        if inspect.isabstract(implementation):
            raise ProviderRegistrationException(
                f'{implementation.__name__} is abstract and cannot be registered.'
            )
        missing = getattr(implementation, '__abstractmethods__', set())
        if missing:
            raise ProviderRegistrationException(
                f'{implementation.__name__} is missing implementations for: {sorted(missing)}'
            )

        signature_errors = []
        for method_name in getattr(interface, '__abstractmethods__', set()):
            if not hasattr(implementation, method_name):
                signature_errors.append(f'missing method {method_name}')
                continue
            expected = inspect.signature(getattr(interface, method_name))
            actual = inspect.signature(getattr(implementation, method_name))
            if str(expected) != str(actual):
                signature_errors.append(
                    f'{method_name} signature mismatch {actual} != {expected}'
                )
        if signature_errors:
            raise ProviderRegistrationException(' ; '.join(signature_errors))

    @classmethod
    def _assert_instantiable(cls, provider: ServiceProvider) -> None:
        implementation = provider.implementation
        signature = inspect.signature(implementation)
        params = list(signature.parameters.values())[1:]
        if any(param.default is inspect.Parameter.empty and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD) for param in params):
            if not any(param.kind == inspect.Parameter.VAR_KEYWORD for param in params):
                raise ProviderRegistrationException(
                    f'{implementation.__name__} cannot be instantiated automatically: init requires parameters {params}'
                )
        try:
            if all(param.default is not inspect.Parameter.empty or param.kind == inspect.Parameter.VAR_KEYWORD for param in params):
                implementation()
        except Exception as exc:
            raise ProviderRegistrationException(
                f'{implementation.__name__} failed instantiation validation: {exc}'
            ) from exc

    @classmethod
    def _assert_dependencies(cls, provider: ServiceProvider) -> None:
        for dependency in provider.dependencies:
            try:
                importlib.import_module(dependency)
            except ImportError as exc:
                raise ProviderCompatibilityException(
                    f'Provider {provider.provider_name} requires missing dependency {dependency}'
                ) from exc

    @classmethod
    def _assert_project_compatibility(cls, provider: ServiceProvider) -> None:
        if provider.compatibility is None:
            return

        project_version = None
        try:
            from django.conf import settings
            project_version = getattr(settings, 'PROJECT_VERSION', None)
        except Exception:
            project_version = None

        if project_version is None:
            logger.debug(
                'No PROJECT_VERSION configured; skipping compatibility check for %s',
                provider.provider_name,
            )
            return

        try:
            from packaging.version import Version
            from packaging.specifiers import SpecifierSet
        except ImportError:
            logger.warning(
                'packaging not installed; skipping compatibility check for %s',
                provider.provider_name,
            )
            return

        specifier = SpecifierSet(provider.compatibility)
        if not specifier.contains(Version(str(project_version))):
            raise ProviderCompatibilityException(
                f'Provider {provider.provider_name} is incompatible with project version {project_version}'
            )

    @classmethod
    def _assert_active_provider(cls, interface: Type[ServiceInterface]) -> None:
        active = [provider for provider in cls._registry.get(interface, {}).values() if provider.active]
        if not active:
            raise ProviderNotFoundException(
                f'No active providers remain for interface {interface.__name__}'
            )

    @classmethod
    def _find_service_interface(cls, implementation: Type[ServiceInterface]) -> Optional[Type[ServiceInterface]]:
        for base in inspect.getmro(implementation):
            if base is implementation or base is ServiceInterface:
                continue
            if not inspect.isclass(base):
                continue
            if not issubclass(base, ServiceInterface):
                continue
            if base.__module__.startswith('devops.services.interfaces'):
                return base
        return None


def provider(interface: Type[ServiceInterface], provider_name: Optional[str] = None):
    """Decorator that registers a provider implementation for a given interface."""

    def decorator(implementation: Type[ServiceInterface]) -> Type[ServiceInterface]:
        selected_provider = provider_name or getattr(implementation, 'provider_name', None)
        if not selected_provider:
            raise ProviderRegistrationException(
                f'Provider name is required when registering {implementation.__name__}'
            )
        ProviderRegistry.register(interface, selected_provider, implementation)
        return implementation

    return decorator
