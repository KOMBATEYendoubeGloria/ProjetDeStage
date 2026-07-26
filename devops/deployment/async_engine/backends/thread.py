"""Thread-pool job execution backend."""

from __future__ import annotations

import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

from .base import JobBackend

logger = logging.getLogger(__name__)


class ThreadJobBackend(JobBackend):
    """Job backend using Python's ThreadPoolExecutor.

    Thread-safe. Cancellation is cooperative via threading.Event.
    """

    def __init__(self, max_workers: int = 4):
        self._pool = ThreadPoolExecutor(max_workers=max_workers)
        self._futures: Dict[str, Future] = {}
        self._cancelled: Dict[str, threading.Event] = {}
        self._lock = threading.RLock()

    def submit(self, job_id: str, job_fn: Callable[[], Any]) -> None:
        event = threading.Event()
        with self._lock:
            self._cancelled[job_id] = event

        def _wrapper():
            if event.is_set():
                return None
            return job_fn()

        future = self._pool.submit(_wrapper)
        with self._lock:
            self._futures[job_id] = future
        logger.info('ThreadJobBackend: submitted job %s', job_id)

    def cancel(self, job_id: str) -> None:
        with self._lock:
            event = self._cancelled.get(job_id)
        if event:
            event.set()
            logger.info('ThreadJobBackend: cancellation requested for job %s', job_id)

    def is_cancelled(self, job_id: str) -> bool:
        with self._lock:
            event = self._cancelled.get(job_id)
        return event.is_set() if event else False

    def get_job_status(self, job_id: str) -> Optional[str]:
        with self._lock:
            future = self._futures.get(job_id)
            event = self._cancelled.get(job_id)
        if future is None:
            return None
        if event and event.is_set():
            return 'CANCELLED'
        if future.done():
            return 'COMPLETED'
        return 'RUNNING'

    def list_jobs(self) -> Dict[str, str]:
        with self._lock:
            return {
                jid: self.get_job_status(jid)
                for jid in self._futures
            }

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool."""
        self._pool.shutdown(wait=wait)
