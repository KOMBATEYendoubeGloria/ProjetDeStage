from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .base import ServiceInterface
from ...exceptions import ValidationException


class ValidatorInterface(ServiceInterface):
    """Abstract contract for resource validation.

    Responsibilities:
        - Validate domain resources and configuration.
    Excluded responsibilities:
        - Validation implementation details.
    """

    @abstractmethod
    def validate(self, payload: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Validate payload and return a list of validation issues."""
        raise ValidationException('validate not implemented')

    @abstractmethod
    def is_valid(self, payload: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> bool:
        """Return whether the payload is valid."""
        raise ValidationException('is_valid not implemented')
