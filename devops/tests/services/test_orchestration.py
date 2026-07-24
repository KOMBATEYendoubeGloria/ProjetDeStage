from django.test import SimpleTestCase
from devops.exceptions import DeploymentException, PipelineException
from devops.services.implementations.deployment.default import DefaultDeploymentService
from devops.services.implementations.pipeline.default import DefaultPipelineService


class DeploymentServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultDeploymentService()

    def test_prepare_execute_and_cancel(self):
        self.service.prepare('deploy1', metadata={'project_id': 'p1'})
        result = self.service.execute('deploy1', parameters={'flag': True})
        self.assertEqual(result['status'], 'running')
        status = self.service.status('deploy1')
        self.assertEqual(status['status'], 'running')
        self.service.cancel('deploy1')
        self.assertEqual(self.service.status('deploy1')['status'], 'cancelled')

    def test_status_raises_for_missing_deployment(self):
        with self.assertRaises(DeploymentException):
            self.service.status('missing')

    def test_list_deployments_filters_by_project(self):
        self.service.prepare('deploy2', metadata={'project_id': 'p2'})
        result = self.service.list_deployments(project_id='p2')
        self.assertEqual(len(result), 1)


class PipelineServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DefaultPipelineService()

    def test_create_execute_and_status(self):
        pipeline_id = self.service.create_pipeline({'id': 'pipe1', 'name': 'pipe1'})
        self.assertEqual(pipeline_id, 'pipe1')
        run = self.service.execute_pipeline('pipe1', parameters={'x': 1})
        self.assertEqual(run['status'], 'succeeded')
        status = self.service.get_pipeline_status('pipe1')
        self.assertEqual(status['pipeline_id'], 'pipe1')
        runs = self.service.list_pipeline_runs('pipe1')
        self.assertEqual(len(runs), 1)

    def test_execute_pipeline_raises_for_unknown(self):
        with self.assertRaises(PipelineException):
            self.service.execute_pipeline('missing')
