"""Tests for Phase 9 DevOps API serializers."""

from django.test import SimpleTestCase

from devops.api.serializers.project_analysis import ProjectAnalysisSerializer
from devops.api.serializers.artifact_generation import ArtifactGenerationSerializer
from devops.api.serializers.deployment import DeploymentSerializer
from devops.api.serializers.provider import ProviderSerializer
from devops.api.serializers.generation_history import GenerationHistorySerializer


# ---------------------------------------------------------------------------
# ProjectAnalysisSerializer
# ---------------------------------------------------------------------------
class ProjectAnalysisSerializerTests(SimpleTestCase):
    def test_valid_with_name(self):
        s = ProjectAnalysisSerializer(data={'name': 'myapp'})
        self.assertTrue(s.is_valid(), s.errors)

    def test_valid_with_path(self):
        s = ProjectAnalysisSerializer(data={'path': '/tmp/project'})
        self.assertTrue(s.is_valid(), s.errors)

    def test_valid_with_all_fields(self):
        s = ProjectAnalysisSerializer(data={
            'name': 'myapp',
            'framework': 'django',
            'language': 'python',
            'version': '3.11',
            'ports': [8000],
            'database': 'postgres',
            'provider': 'docker',
            'ci_platform': 'github-actions',
            'environment': 'dev',
        })
        self.assertTrue(s.is_valid(), s.errors)

    def test_missing_name_and_path_fails(self):
        s = ProjectAnalysisSerializer(data={})
        self.assertFalse(s.is_valid())

    def test_invalid_framework_rejected(self):
        s = ProjectAnalysisSerializer(data={'name': 'x', 'framework': 'rails'})
        self.assertFalse(s.is_valid())

    def test_invalid_provider_rejected(self):
        s = ProjectAnalysisSerializer(data={'name': 'x', 'provider': 'aws'})
        self.assertFalse(s.is_valid())

    def test_invalid_ci_platform_rejected(self):
        s = ProjectAnalysisSerializer(data={'name': 'x', 'ci_platform': 'circleci'})
        self.assertFalse(s.is_valid())

    def test_invalid_port_range_rejected(self):
        s = ProjectAnalysisSerializer(data={'name': 'x', 'ports': [99999]})
        self.assertFalse(s.is_valid())


# ---------------------------------------------------------------------------
# ArtifactGenerationSerializer
# ---------------------------------------------------------------------------
class ArtifactGenerationSerializerTests(SimpleTestCase):
    def test_valid_minimal(self):
        s = ArtifactGenerationSerializer(data={'name': 'app', 'framework': 'django'})
        self.assertTrue(s.is_valid(), s.errors)

    def test_valid_full(self):
        s = ArtifactGenerationSerializer(data={
            'name': 'demo-app',
            'type': 'django',
            'framework': 'django',
            'language': 'python',
            'version': '3.11',
            'ports': [8000],
            'environment': 'dev',
            'docker_image': 'demo:latest',
            'database': 'postgres',
            'redis': True,
            'provider': 'docker',
            'ci_platform': 'github-actions',
        })
        self.assertTrue(s.is_valid(), s.errors)

    def test_missing_name_fails(self):
        s = ArtifactGenerationSerializer(data={'framework': 'django'})
        self.assertFalse(s.is_valid())

    def test_missing_framework_fails(self):
        s = ArtifactGenerationSerializer(data={'name': 'app'})
        self.assertFalse(s.is_valid())

    def test_blank_name_rejected(self):
        s = ArtifactGenerationSerializer(data={'name': '   ', 'framework': 'django'})
        self.assertFalse(s.is_valid())

    def test_blank_name_stripped(self):
        s = ArtifactGenerationSerializer(data={'name': '  myapp  ', 'framework': 'django'})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data['name'], 'myapp')


# ---------------------------------------------------------------------------
# DeploymentSerializer
# ---------------------------------------------------------------------------
class DeploymentSerializerTests(SimpleTestCase):
    def test_valid_minimal(self):
        s = DeploymentSerializer(data={'project_id': 1, 'environment': 'dev'})
        self.assertTrue(s.is_valid(), s.errors)

    def test_valid_full(self):
        s = DeploymentSerializer(data={
            'project_id': 1,
            'environment': 'prod',
            'target': 'vm-01',
            'commit_hash': 'abc123',
            'metadata': {'branch': 'main'},
        })
        self.assertTrue(s.is_valid(), s.errors)

    def test_missing_project_id_fails(self):
        s = DeploymentSerializer(data={'environment': 'dev'})
        self.assertFalse(s.is_valid())

    def test_invalid_environment_fails(self):
        s = DeploymentSerializer(data={'project_id': 1, 'environment': 'invalid'})
        self.assertFalse(s.is_valid())


# ---------------------------------------------------------------------------
# ProviderSerializer
# ---------------------------------------------------------------------------
class ProviderSerializerTests(SimpleTestCase):
    def test_valid_docker(self):
        s = ProviderSerializer(data={'provider': 'docker'})
        self.assertTrue(s.is_valid(), s.errors)

    def test_valid_with_config(self):
        s = ProviderSerializer(data={
            'provider': 'proxmox',
            'config': {'endpoint': 'https://pm.local:8006'},
        })
        self.assertTrue(s.is_valid(), s.errors)

    def test_invalid_provider_fails(self):
        s = ProviderSerializer(data={'provider': 'aws'})
        self.assertFalse(s.is_valid())


# ---------------------------------------------------------------------------
# GenerationHistorySerializer
# ---------------------------------------------------------------------------
class GenerationHistorySerializerTests(SimpleTestCase):
    def test_read_only_fields(self):
        fields = GenerationHistorySerializer().fields
        for field_name in [
            'id', 'project_name', 'framework', 'provider',
            'ci_platform', 'artifacts_generated', 'status', 'created_at',
        ]:
            self.assertIn(field_name, fields)
            self.assertTrue(fields[field_name].read_only)
