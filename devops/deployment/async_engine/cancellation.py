"""Cooperative cancellation token for async deployment jobs."""

from __future__ import annotations

import threading


class CancellationToken:
    """Thread-safe cooperative cancellation signal.

    Cancellation is checked at safe checkpoints (stage boundaries).
    Running subprocesses (terraform, docker, ansible) are not interrupted.
    """

    def __init__(self):
        self._event = threading.Event()

    def cancel(self) -> None:
        """Request cancellation."""
        self._event.set()

    @property
    def cancelled(self) -> bool:
        """Return True if cancellation was requested."""
        return self._event.is_set()

    def throw_if_cancelled(self) -> None:
        """Raise CancellationError if cancellation was requested.

        Use at safe checkpoints to abort the current operation.
        """
        if self._event.is_set():
            raise CancellationError('Deployment cancelled by user')

    @property
    def is_cancelled(self) -> bool:
        """Alias for cancelled property (callable form)."""
        return self._event.is_set()


class CancellationError(Exception):
    """Raised when a cancelled operation is interrupted at a safe checkpoint."""
