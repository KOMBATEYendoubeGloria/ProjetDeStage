from django.test import SimpleTestCase

from devops.orchestrator import DeploymentOrchestrator, ExecutionContext, WorkflowDefinition, WorkflowException, WorkflowStep
from devops.orchestrator.execution_state import WorkflowState


class OrchestratorEngineTests(SimpleTestCase):
    def test_workflow_execute_success(self):
        def step_one(context: ExecutionContext):
            context.record_output('step_one', 'ok')
            return {'status': 'done'}

        def step_two(context: ExecutionContext):
            context.record_output('step_two', 'ok')
            return {'status': 'done'}

        workflow_definition = WorkflowDefinition(
            workflow_id='wf-success',
            name='Success workflow',
            steps=[
                WorkflowStep(step_id='one', name='Step One', action=step_one),
                WorkflowStep(step_id='two', name='Step Two', action=step_two),
            ],
        )
        context = ExecutionContext(
            workflow_id='wf-success',
            user_id='user1',
            project_id='project1',
            environment='dev',
            provider_name=None,
        )

        orchestrator = DeploymentOrchestrator()
        result = orchestrator.execute(workflow_definition, context)

        self.assertEqual(result['state'], WorkflowState.COMPLETED)
        self.assertEqual(result['progress'], 100.0)
        self.assertEqual(result['outputs'], {'step_one': 'ok', 'step_two': 'ok'})

    def test_workflow_execute_failure_triggers_rollback(self):
        def step_one(context: ExecutionContext):
            context.record_output('step_one', 'ok')
            return {'status': 'done'}

        def rollback_step_one(context: ExecutionContext):
            context.record_output('step_one_rollback', True)

        def failing_step(context: ExecutionContext):
            raise RuntimeError('simulated failure')

        workflow_definition = WorkflowDefinition(
            workflow_id='wf-failure',
            name='Failure workflow',
            steps=[
                WorkflowStep(step_id='one', name='Step One', action=step_one, rollback_action=rollback_step_one),
                WorkflowStep(step_id='two', name='Step Two', action=failing_step),
            ],
        )
        context = ExecutionContext(
            workflow_id='wf-failure',
            user_id='user2',
            project_id='project2',
            environment='staging',
            provider_name=None,
            metadata={'rollbackable_steps': {'one': rollback_step_one}},
        )

        orchestrator = DeploymentOrchestrator()

        with self.assertRaises(WorkflowException):
            orchestrator.execute(workflow_definition, context)

        self.assertEqual(context.outputs.get('step_one'), 'ok')
        self.assertTrue(context.outputs.get('step_one_rollback'))
