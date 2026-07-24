"""Deployment profile support for the configuration engine."""

from __future__ import annotations

import logging
from typing import Any, Dict

from ...exceptions import ConfigurationException
from ..manager.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class DeploymentProfileManager:
    """Manage named deployment profiles."""

    def __init__(self, configuration_manager: ConfigurationManager) -> None:
        self._configuration_manager = configuration_manager

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        return self._configuration_manager.get_deployment_profile(profile_name)

    def apply_profile(self, profile_name: str, base_configuration: Dict[str, Any]) -> Dict[str, Any]:
        profile = self.get_profile(profile_name)
        merged = {**base_configuration, **profile}
        logger.info('Applied deployment profile %s', profile_name)
        return merged

    def validate_profile(self, profile_name: str) -> bool:
        try:
            self.get_profile(profile_name)
            return True
        except ConfigurationException:
            return False
