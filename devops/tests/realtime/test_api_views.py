"""Tests for deployment monitoring API views."""

import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from devops.models import DeploymentJob, DeploymentLogEntry, DeploymentEvent


@override_settings(SECURE_SSL_REDIRECT=False)
class AsyncDeploymentStartViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = '/devops/api/deployment/async/start/'

    def test_start_deployment_success(self):
        payload = {
            'provider_name': 'docker',
            'project': {'name': 'test-app', 'type': 'web'},
            'artifacts': {'dockerfile': 'FROM python:3.11'},
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('deployment_id', data['data'])

    def test_start_deployment_invalid_serializer(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])

    def test_start_deployment_missing_project(self):
        payload = {
            'provider_name': 'docker',
            'artifacts': {'dockerfile': 'FROM python:3.11'},
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])


@override_settings(SECURE_SSL_REDIRECT=False)
class AsyncDeploymentStatusViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_status_found(self):
        job = DeploymentJob.objects.create(
            deployment_id=uuid.uuid4(),
            provider_name='docker',
            project_data={'name': 'test'},
            artifacts_data={},
            status='RUNNING',
            current_stage='VALIDATION',
            progress_percent=5,
        )
        url = f'/devops/api/deployment/async/{job.deployment_id}/status/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['deployment_id'], str(job.deployment_id))

    def test_status_not_found(self):
        fake_id = uuid.uuid4()
        url = f'/devops/api/deployment/async/{fake_id}/status/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])


@override_settings(SECURE_SSL_REDIRECT=False)
class AsyncDeploymentCancelViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_cancel(self):
        job = DeploymentJob.objects.create(
            deployment_id=uuid.uuid4(),
            provider_name='docker',
            project_data={'name': 'test'},
            artifacts_data={},
            status='RUNNING',
        )
        url = f'/devops/api/deployment/async/{job.deployment_id}/cancel/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])


@override_settings(SECURE_SSL_REDIRECT=False)
class AsyncDeploymentLogsViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_logs_found(self):
        job = DeploymentJob.objects.create(
            deployment_id=uuid.uuid4(),
            provider_name='docker',
            project_data={'name': 'test'},
            artifacts_data={},
            status='COMPLETED',
        )
        DeploymentLogEntry.objects.create(job=job, message='Log 1', level='INFO')
        DeploymentLogEntry.objects.create(job=job, message='Log 2', level='WARNING')
        url = f'/devops/api/deployment/async/{job.deployment_id}/logs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['logs']), 2)

    def test_logs_not_found(self):
        fake_id = uuid.uuid4()
        url = f'/devops/api/deployment/async/{fake_id}/logs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])


@override_settings(SECURE_SSL_REDIRECT=False)
class AsyncDeploymentEventsViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_events_found(self):
        job = DeploymentJob.objects.create(
            deployment_id=uuid.uuid4(),
            provider_name='docker',
            project_data={'name': 'test'},
            artifacts_data={},
            status='COMPLETED',
        )
        DeploymentEvent.objects.create(job=job, event_type='started', payload={})
        url = f'/devops/api/deployment/async/{job.deployment_id}/events/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['events']), 1)

    def test_events_not_found(self):
        fake_id = uuid.uuid4()
        url = f'/devops/api/deployment/async/{fake_id}/events/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])


@override_settings(SECURE_SSL_REDIRECT=False)
class AsyncDeploymentListViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_list_empty(self):
        response = self.client.get('/devops/api/deployment/async/list/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['jobs'], [])

    def test_list_with_jobs(self):
        DeploymentJob.objects.create(
            deployment_id=uuid.uuid4(),
            provider_name='docker',
            project_data={'name': 'test'},
            artifacts_data={},
            status='COMPLETED',
        )
        response = self.client.get('/devops/api/deployment/async/list/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['data']['jobs']), 1)
