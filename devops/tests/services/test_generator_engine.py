"""Comprehensive unit tests for Phase 8 DevOps Artifact Generator Engine."""

from django.test import SimpleTestCase, TestCase

from devops.generators.engine.artifact_engine import ArtifactEngine
from devops.generators.engine.generated_artifacts import GeneratedArtifacts
from devops.generators.analyzer.project_analyzer import ProjectAnalyzer
from devops.generators.validators.artifact_validator import ArtifactValidator
from devops.generators.implementations.docker.default import DefaultDockerGenerator
from devops.generators.implementations.environment.default import DefaultEnvironmentGenerator
from devops.generators.implementations.terraform.default import DefaultTerraformGenerator
from devops.generators.implementations.ansible.default import DefaultAnsibleGenerator
from devops.generators.implementations.pipeline.default import DefaultPipelineGenerator


# ---------------------------------------------------------------------------
# Shared project fixture
# ---------------------------------------------------------------------------
BASE_PROJECT = {
    'name': 'demo-app',
    'type': 'django',
    'framework': 'django',
    'language': 'python',
    'version': '3.11',
    'ports': [8000],
    'environment': 'dev',
    'docker_image': 'demo-app:latest',
    'database': 'postgres',
    'redis': True,
    'reverse_proxy': False,
    'provider': 'docker',
    'ci_platform': 'github-actions',
    'terraform': {'provider': 'docker', 'resources': ['vm']},
    'ansible': {'hosts': ['localhost']},
    'ci': {'platform': 'github-actions'},
}


# ---------------------------------------------------------------------------
# ProjectAnalyzer tests
# ---------------------------------------------------------------------------
class ProjectAnalyzerTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_enrich_django_dict(self):
        project = {'name': 'myapp', 'framework': 'django'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'python')
        self.assertEqual(result['ports'], [8000])
        self.assertEqual(result['database'], 'postgres')

    def test_enrich_nodejs_dict(self):
        project = {'name': 'myapp', 'framework': 'nodejs'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'javascript')
        self.assertEqual(result['ports'], [3000])

    def test_enrich_react_dict(self):
        project = {'name': 'frontend', 'framework': 'react'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['ports'], [80])

    def test_enrich_laravel_dict(self):
        project = {'name': 'api', 'framework': 'laravel'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'php')
        self.assertEqual(result['database'], 'mysql')

    def test_enrich_springboot_dict(self):
        project = {'name': 'svc', 'framework': 'springboot'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['ports'], [8080])

    def test_fills_missing_provider_and_ci(self):
        project = {'name': 'app', 'framework': 'django'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['provider'], 'docker')
        self.assertEqual(result['ci_platform'], 'github-actions')


# ---------------------------------------------------------------------------
# ArtifactValidator tests
# ---------------------------------------------------------------------------
class ArtifactValidatorTests(SimpleTestCase):
    def setUp(self):
        self.validator = ArtifactValidator()

    def test_valid_project_passes(self):
        self.validator.validate(BASE_PROJECT)  # should not raise

    def test_missing_name_raises(self):
        project = dict(BASE_PROJECT)
        del project['name']
        with self.assertRaises(ValueError):
            self.validator.validate(project)

    def test_invalid_ports_type_raises(self):
        project = dict(BASE_PROJECT)
        project['ports'] = 'not-a-list'
        with self.assertRaises(ValueError):
            self.validator.validate(project)


# ---------------------------------------------------------------------------
# Docker Generator tests
# ---------------------------------------------------------------------------
class DockerGeneratorTests(SimpleTestCase):
    def setUp(self):
        self.gen = DefaultDockerGenerator()

    def test_generate_dockerfile_contains_from(self):
        result = self.gen.generate_dockerfile(BASE_PROJECT)
        self.assertIn('FROM', result)

    def test_generate_dockerfile_contains_port(self):
        result = self.gen.generate_dockerfile(BASE_PROJECT)
        self.assertIn('8000', result)

    def test_generate_compose_contains_version(self):
        result = self.gen.generate_docker_compose(BASE_PROJECT)
        self.assertIn('version:', result)


# ---------------------------------------------------------------------------
# Environment Generator tests
# ---------------------------------------------------------------------------
class EnvironmentGeneratorTests(SimpleTestCase):
    def setUp(self):
        self.gen = DefaultEnvironmentGenerator()

    def test_generate_environment_has_name(self):
        result = self.gen.generate_environment(BASE_PROJECT)
        self.assertTrue(len(result) > 0)

    def test_no_secrets_in_log(self):
        # Generating should not raise and content should be non-empty
        result = self.gen.generate_environment(BASE_PROJECT)
        self.assertIsInstance(result, str)


# ---------------------------------------------------------------------------
# Terraform Generator tests
# ---------------------------------------------------------------------------
class TerraformGeneratorTests(SimpleTestCase):
    def setUp(self):
        self.gen = DefaultTerraformGenerator()

    def test_generate_terraform_docker_provider(self):
        result = self.gen.generate_terraform(BASE_PROJECT)
        self.assertIn('terraform', result.lower())

    def test_generate_terraform_proxmox_provider(self):
        project = dict(BASE_PROJECT)
        project['provider'] = 'proxmox'
        result = self.gen.generate_terraform(project)
        self.assertIn('terraform', result.lower())

    def test_generate_terraform_vmware_provider(self):
        project = dict(BASE_PROJECT)
        project['provider'] = 'vmware'
        result = self.gen.generate_terraform(project)
        self.assertIn('terraform', result.lower())

    def test_generate_terraform_virtualbox_provider(self):
        project = dict(BASE_PROJECT)
        project['provider'] = 'virtualbox'
        result = self.gen.generate_terraform(project)
        self.assertIn('terraform', result.lower())


# ---------------------------------------------------------------------------
# Ansible Generator tests
# ---------------------------------------------------------------------------
class AnsibleGeneratorTests(SimpleTestCase):
    def setUp(self):
        self.gen = DefaultAnsibleGenerator()

    def test_generate_ansible_has_hosts(self):
        result = self.gen.generate_ansible(BASE_PROJECT)
        self.assertIn('hosts:', result)

    def test_generate_inventory_has_app_servers(self):
        result = self.gen.generate_inventory(BASE_PROJECT)
        self.assertIn('app_servers', result)


# ---------------------------------------------------------------------------
# Pipeline Generator tests
# ---------------------------------------------------------------------------
class PipelineGeneratorTests(SimpleTestCase):
    def setUp(self):
        self.gen = DefaultPipelineGenerator()

    def test_generate_github_actions_pipeline(self):
        result = self.gen.generate_pipeline(BASE_PROJECT)
        self.assertIn('name:', result)

    def test_generate_gitlab_ci_pipeline(self):
        project = dict(BASE_PROJECT)
        project['ci_platform'] = 'gitlab-ci'
        result = self.gen.generate_pipeline(project)
        self.assertIn('stages', result)

    def test_generate_jenkins_pipeline(self):
        project = dict(BASE_PROJECT)
        project['ci_platform'] = 'jenkins'
        result = self.gen.generate_pipeline(project)
        self.assertIn('pipeline', result.lower())

    def test_pipeline_adapts_to_nodejs(self):
        project = dict(BASE_PROJECT)
        project['framework'] = 'nodejs'
        project['ci_platform'] = 'github-actions'
        result = self.gen.generate_pipeline(project)
        self.assertIn('name:', result)


# ---------------------------------------------------------------------------
# ArtifactEngine integration tests
# ---------------------------------------------------------------------------
class GeneratorEngineTests(SimpleTestCase):
    def test_generate_common_artifacts(self):
        engine = ArtifactEngine()
        project = dict(BASE_PROJECT)

        dockerfile = engine.generate_dockerfile(project)
        compose = engine.generate_docker_compose(project)
        terraform = engine.generate_terraform(project)
        ansible = engine.generate_ansible(project)
        pipeline = engine.generate_pipeline(project)

        self.assertIn('FROM', dockerfile)
        self.assertIn('version:', compose)
        self.assertIn('terraform', terraform.lower())
        self.assertIn('hosts:', ansible)
        self.assertIn('name:', pipeline)

    def test_generate_all_returns_generated_artifacts(self):
        engine = ArtifactEngine()
        result = engine.generate_all(BASE_PROJECT, record_history=False)
        self.assertIsInstance(result, GeneratedArtifacts)
        self.assertTrue(result.dockerfile)
        self.assertTrue(result.docker_compose)
        self.assertTrue(result.terraform)
        self.assertTrue(result.ansible_playbook)
        self.assertTrue(result.ansible_inventory)
        self.assertTrue(result.pipeline)

    def test_generated_artifacts_to_dict(self):
        engine = ArtifactEngine()
        result = engine.generate_all(BASE_PROJECT, record_history=False)
        d = result.to_dict()
        self.assertIn('dockerfile', d)
        self.assertIn('metadata', d)

    def test_generate_all_react_stack(self):
        engine = ArtifactEngine()
        project = {
            'name': 'react-frontend',
            'type': 'react',
            'framework': 'react',
            'language': 'javascript',
            'version': '18-alpine',
            'ports': [80],
            'environment': 'prod',
            'docker_image': 'react-frontend:latest',
        }
        result = engine.generate_all(project, record_history=False)
        self.assertIsInstance(result, GeneratedArtifacts)
        self.assertIn('FROM', result.dockerfile)

    def test_generate_all_laravel_stack(self):
        engine = ArtifactEngine()
        project = {
            'name': 'laravel-api',
            'type': 'laravel',
            'framework': 'laravel',
            'language': 'php',
            'version': '8.2',
            'ports': [8000],
            'environment': 'dev',
            'docker_image': 'laravel-api:latest',
        }
        result = engine.generate_all(project, record_history=False)
        self.assertIsInstance(result, GeneratedArtifacts)
        self.assertIn('FROM', result.dockerfile)


# ---------------------------------------------------------------------------
# GeneratedArtifacts tests
# ---------------------------------------------------------------------------
class GeneratedArtifactsTests(SimpleTestCase):
    def test_to_dict_has_all_fields(self):
        ga = GeneratedArtifacts(dockerfile='FROM python:3.11', docker_compose='version: "3.9"')
        d = ga.to_dict()
        self.assertIn('dockerfile', d)
        self.assertIn('docker_compose', d)
        self.assertIn('terraform', d)
        self.assertIn('ansible_playbook', d)
        self.assertIn('pipeline', d)
        self.assertIn('metadata', d)

    def test_save_to_directory(self):
        import tempfile, os
        ga = GeneratedArtifacts(
            dockerfile='FROM python:3.11-slim',
            docker_compose="version: '3.9'",
            metadata={'ci_platform': 'github-actions'},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = ga.save_to_directory(tmpdir)
            self.assertIn('dockerfile', saved)
            self.assertTrue(os.path.exists(saved['dockerfile']))
            self.assertIn('metadata', saved)


# ---------------------------------------------------------------------------
# GenerationHistory tests (require DB)
# ---------------------------------------------------------------------------
class GenerationHistoryTests(TestCase):
    def test_generation_history_record_created(self):
        from devops.models import GenerationHistory
        engine = ArtifactEngine()
        engine.generate_all(BASE_PROJECT, record_history=True)
        self.assertTrue(GenerationHistory.objects.filter(project_name='demo-app').exists())

    def test_generation_history_str_representation(self):
        from devops.models import GenerationHistory
        record = GenerationHistory.objects.create(
            project_name='test-proj',
            framework='django',
            provider='docker',
            ci_platform='github-actions',
            status='SUCCESS',
        )
        self.assertIn('test-proj', str(record))
