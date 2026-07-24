"""Tests for Phase 9 DevOps API views and HTTP responses."""

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from devops.models import GenerationHistory


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------
BASE_PROJECT = {
    'name': 'test-app',
    'type': 'django',
    'framework': 'django',
    'language': 'python',
    'version': '3.11',
    'ports': [8000],
    'environment': 'dev',
    'docker_image': 'test-app:latest',
    'database': 'postgres',
    'redis': True,
    'provider': 'docker',
    'ci_platform': 'github-actions',
}

ANALYZE_URL = '/devops/api/analyze/'
HEALTH_URL = '/devops/api/health/'
HISTORY_URL = '/devops/api/history/'


def _artifact_url(artifact_type):
    return f'/devops/api/artifacts/{artifact_type}/'


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------
class HealthCheckViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_returns_200(self):
        response = self.client.get(HEALTH_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['api'], 'healthy')
        self.assertEqual(response.data['data']['database'], 'healthy')

    def test_health_response_structure(self):
        response = self.client.get(HEALTH_URL)
        body = response.data
        self.assertIn('success', body)
        self.assertIn('message', body)
        self.assertIn('data', body)
        self.assertIn('errors', body)
        self.assertIn('timestamp', body)
        self.assertIn('request_id', body)

    def test_health_post_not_allowed(self):
        response = self.client.post(HEALTH_URL, {})
        self.assertIn(response.status_code, [405, 403])


# ---------------------------------------------------------------------------
# Analyze endpoint
# ---------------------------------------------------------------------------
class AnalyzeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_analyze_with_name(self):
        response = self.client.post(ANALYZE_URL, {'name': 'myapp'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertIn('framework', response.data['data'])
        self.assertIn('language', response.data['data'])
        self.assertIn('ports', response.data['data'])

    def test_analyze_with_framework_override(self):
        response = self.client.post(
            ANALYZE_URL,
            {'name': 'svc', 'framework': 'springboot'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['framework'], 'springboot')
        self.assertEqual(response.data['data']['language'], 'java')

    def test_analyze_empty_body_fails(self):
        response = self.client.post(ANALYZE_URL, {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
        self.assertTrue(len(response.data['errors']) > 0)

    def test_analyze_invalid_framework_fails(self):
        response = self.client.post(
            ANALYZE_URL,
            {'name': 'x', 'framework': 'rails'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])

    def test_analyze_response_structure(self):
        response = self.client.post(ANALYZE_URL, {'name': 'app'}, format='json')
        body = response.data
        self.assertIn('success', body)
        self.assertIn('message', body)
        self.assertIn('data', body)
        self.assertIn('errors', body)
        self.assertIn('timestamp', body)
        self.assertIn('request_id', body)


# ---------------------------------------------------------------------------
# Individual artifact endpoints
# ---------------------------------------------------------------------------
class DockerfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_generate_dockerfile(self):
        response = self.client.post(
            _artifact_url('docker'),
            BASE_PROJECT,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        content = response.data['data']['generate_dockerfile']
        self.assertIn('FROM', content)

    def test_generate_dockerfile_missing_name(self):
        response = self.client.post(
            _artifact_url('docker'),
            {'framework': 'django'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])


class DockerComposeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_generate_compose(self):
        response = self.client.post(
            _artifact_url('docker-compose'),
            BASE_PROJECT,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        content = response.data['data']['generate_docker_compose']
        self.assertIn('version:', content)


class EnvironmentViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_generate_environment(self):
        response = self.client.post(
            _artifact_url('environment'),
            BASE_PROJECT,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        content = response.data['data']['generate_environment']
        self.assertIsInstance(content, str)
        self.assertTrue(len(content) > 0)


class TerraformViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_generate_terraform(self):
        response = self.client.post(
            _artifact_url('terraform'),
            BASE_PROJECT,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        content = response.data['data']['generate_terraform']
        self.assertIn('terraform', content.lower())


class AnsibleViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_generate_ansible(self):
        response = self.client.post(
            _artifact_url('ansible'),
            BASE_PROJECT,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        content = response.data['data']['generate_ansible']
        self.assertIn('hosts:', content)


class PipelineViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_generate_pipeline(self):
        response = self.client.post(
            _artifact_url('pipeline'),
            BASE_PROJECT,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        content = response.data['data']['generate_pipeline']
        self.assertIn('name:', content)


# ---------------------------------------------------------------------------
# All artifacts endpoint
# ---------------------------------------------------------------------------
class AllArtifactsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_generate_all(self):
        response = self.client.post(
            _artifact_url('all'),
            BASE_PROJECT,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        data = response.data['data']
        self.assertIn('dockerfile', data)
        self.assertIn('docker_compose', data)
        self.assertIn('environment', data)
        self.assertIn('terraform', data)
        self.assertIn('ansible_playbook', data)
        self.assertIn('ansible_inventory', data)
        self.assertIn('pipeline', data)
        self.assertIn('metadata', data)

    def test_generate_all_missing_fields(self):
        response = self.client.post(
            _artifact_url('all'),
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])

    def test_generate_all_records_history(self):
        self.client.post(_artifact_url('all'), BASE_PROJECT, format='json')
        self.assertTrue(
            GenerationHistory.objects.filter(project_name='test-app').exists()
        )


# ---------------------------------------------------------------------------
# Generation history endpoints
# ---------------------------------------------------------------------------
class GenerationHistoryListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        GenerationHistory.objects.create(
            project_name='proj-1',
            framework='django',
            provider='docker',
            ci_platform='github-actions',
            status='SUCCESS',
        )

    def test_list_history(self):
        response = self.client.get(HISTORY_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)

    def test_list_history_empty(self):
        GenerationHistory.objects.all().delete()
        response = self.client.get(HISTORY_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'], [])


class GenerationHistoryDetailViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.record = GenerationHistory.objects.create(
            project_name='proj-2',
            framework='nodejs',
            provider='docker',
            status='SUCCESS',
        )

    def test_get_history_detail(self):
        response = self.client.get(f'{HISTORY_URL}{self.record.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['project_name'], 'proj-2')

    def test_get_history_not_found(self):
        response = self.client.get(f'{HISTORY_URL}99999/')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data['success'])


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------
class ErrorHandlingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            ANALYZE_URL,
            'not json',
            content_type='application/json',
        )
        self.assertIn(response.status_code, [400, 415])

    def test_get_on_post_only_endpoint_returns_405(self):
        response = self.client.get(_artifact_url('docker'))
        self.assertIn(response.status_code, [405, 403])

    def test_nonexistent_url_returns_404(self):
        response = self.client.get('/devops/api/nonexistent/')
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# OpenAPI schema
# ---------------------------------------------------------------------------
class OpenAPISchemaTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_schema_accessible(self):
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('openapi', response.data)

    def test_swagger_ui_accessible(self):
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, 200)

    def test_redoc_accessible(self):
        response = self.client.get('/api/redoc/')
        self.assertEqual(response.status_code, 200)
