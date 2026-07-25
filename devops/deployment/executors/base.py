"""Base interface for deployment executors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseExecutor(ABC):
    """Common contract for all deployment executors (Terraform, Ansible, Docker).

    Each executor wraps a single external tool and provides a uniform
    interface for initialization, execution, and teardown.
    """

    executor_name: str = 'base'

    @abstractmethod
    def initialize(self, workspace: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize the executor in the given workspace directory."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, workspace: str, artifacts: Dict[str, Any], variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the deployment using the provided artifacts."""
        raise NotImplementedError

    @abstractmethod
    def teardown(self, workspace: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Destroy or clean up resources created by this executor."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, workspace: str) -> bool:
        """Validate that the executor configuration is correct."""
        raise NotImplementedError

    @abstractmethod
    def get_logs(self) -> List[str]:
        """Return the collected execution logs."""
        raise NotImplementedError
