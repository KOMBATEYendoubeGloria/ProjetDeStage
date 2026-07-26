"""Abstract job execution backend."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional


class JobBackend(ABC):
    """Abstract interface for background job execution backends.

    Concrete implementations may use ThreadPoolExecutor, Celery, RQ, etc.
    The deployment engine depends only on this ABC, never on a concrete backend.
    """

    @abstractmethod
    def submit(self, job_id: str, job_fn: Callable[[], Any]) -> None:
        """Submit a callable for background execution.

        Args:
            job_id: Unique identifier for this job.
            job_fn: Zero-argument callable to execute in background.
        """
        raise NotImplementedError

    @abstractmethod
    def cancel(self, job_id: str) -> None:
        """Request cancellation of a running job.

        The cancellation is cooperative — the job_fn must check
        a cancellation token to honor it.
        """
        raise NotImplementedError

    @abstractmethod
    def is_cancelled(self, job_id: str) -> bool:
        """Check whether cancellation has been requested for this job."""
        raise NotImplementedError

    @abstractmethod
    def get_job_status(self, job_id: str) -> Optional[str]:
        """Return the backend-level status of a job, or None if unknown."""
        raise NotImplementedError

    @abstractmethod
    def list_jobs(self) -> Dict[str, str]:
        """Return {job_id: status} for all tracked jobs."""
        raise NotImplementedError
