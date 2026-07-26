"""Tests for job backends: JobBackend ABC and ThreadJobBackend."""

import time

from django.test import SimpleTestCase

from devops.deployment.async_engine.backends.base import JobBackend
from devops.deployment.async_engine.backends.thread import ThreadJobBackend


class JobBackendABCTests(SimpleTestCase):

    def test_is_abstract(self):
        with self.assertRaises(TypeError):
            JobBackend()

    def test_has_required_methods(self):
        self.assertTrue(hasattr(JobBackend, 'submit'))
        self.assertTrue(hasattr(JobBackend, 'cancel'))
        self.assertTrue(hasattr(JobBackend, 'is_cancelled'))
        self.assertTrue(hasattr(JobBackend, 'get_job_status'))
        self.assertTrue(hasattr(JobBackend, 'list_jobs'))


class ThreadJobBackendTests(SimpleTestCase):

    def setUp(self):
        self._backends = []

    def tearDown(self):
        for b in self._backends:
            b.shutdown(wait=False)

    def _make_backend(self, max_workers=2):
        b = ThreadJobBackend(max_workers=max_workers)
        self._backends.append(b)
        return b

    def test_submit_and_complete(self):
        backend = self._make_backend()
        result = []

        def job():
            result.append('done')

        backend.submit('j1', job)
        time.sleep(0.1)
        self.assertEqual(result, ['done'])
        self.assertEqual(backend.get_job_status('j1'), 'COMPLETED')

    def test_cancel_before_execution(self):
        backend = self._make_backend(max_workers=1)

        def slow_job():
            time.sleep(0.5)

        backend.submit('j1', slow_job)
        backend.cancel('j1')
        self.assertTrue(backend.is_cancelled('j1'))

    def test_get_status_unknown(self):
        backend = self._make_backend()
        self.assertIsNone(backend.get_job_status('unknown'))

    def test_list_jobs(self):
        backend = self._make_backend()
        backend.submit('j1', lambda: None)
        backend.submit('j2', lambda: None)
        time.sleep(0.1)
        jobs = backend.list_jobs()
        self.assertIn('j1', jobs)
        self.assertIn('j2', jobs)

    def test_shutdown(self):
        b = ThreadJobBackend(max_workers=1)
        b.submit('j1', lambda: None)
        time.sleep(0.05)
        b.shutdown(wait=True)

    def test_is_cancelled_unknown_job(self):
        backend = self._make_backend()
        self.assertFalse(backend.is_cancelled('nonexistent'))
