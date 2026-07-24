from django.test import SimpleTestCase

from devops.generators.engine.artifact_engine import ArtifactEngine


class GeneratorEngineTests(SimpleTestCase):
    def test_generate_common_artifacts(self):
        engine = ArtifactEngine()
        project = {
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
            'terraform': {'provider': 'docker', 'resources': ['vm']},
            'ansible': {'hosts': ['localhost']},
            'ci': {'platform': 'github-actions'},
        }

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
