"""Tests for StageTracker."""

from django.test import SimpleTestCase

from devops.deployment.progress.stage_tracker import STAGES, StageTracker


class StageTrackerTests(SimpleTestCase):

    def test_stages_definition(self):
        self.assertEqual(len(STAGES), 8)
        names = [s[0] for s in STAGES]
        self.assertIn('VALIDATION', names)
        self.assertIn('COMPLETED', names)

    def test_calculate_progress_empty(self):
        self.assertEqual(StageTracker.calculate_progress([]), 0)

    def test_calculate_progress_single(self):
        self.assertEqual(StageTracker.calculate_progress(['VALIDATION']), 5)

    def test_calculate_progress_all(self):
        self.assertEqual(StageTracker.calculate_progress([s[0] for s in STAGES]), 100)

    def test_calculate_progress_capped_at_100(self):
        self.assertEqual(StageTracker.calculate_progress([s[0] for s in STAGES] + ['EXTRA']), 100)

    def test_get_stage_info_valid(self):
        info = StageTracker.get_stage_info('VALIDATION')
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'VALIDATION')
        self.assertEqual(info['weight'], 5)
        self.assertEqual(info['order'], 0)

    def test_get_stage_info_invalid(self):
        self.assertIsNone(StageTracker.get_stage_info('NONEXISTENT'))

    def test_get_all_stages(self):
        all_stages = StageTracker.get_all_stages()
        self.assertEqual(len(all_stages), 8)
        self.assertEqual(all_stages[0]['order'], 0)

    def test_get_next_stage(self):
        self.assertEqual(StageTracker.get_next_stage('VALIDATION'), 'PROVISIONING')
        self.assertIsNone(StageTracker.get_next_stage('COMPLETED'))

    def test_get_next_stage_invalid(self):
        self.assertIsNone(StageTracker.get_next_stage('NONEXISTENT'))

    def test_map_phase_to_stage(self):
        self.assertEqual(StageTracker.map_phase_to_stage('initializing'), 'VALIDATION')
        self.assertEqual(StageTracker.map_phase_to_stage('provisioning'), 'PROVISIONING')
        self.assertEqual(StageTracker.map_phase_to_stage('deploying'), 'DOCKER')
        self.assertEqual(StageTracker.map_phase_to_stage('completed'), 'COMPLETED')
        self.assertIsNone(StageTracker.map_phase_to_stage('failed'))
        self.assertIsNone(StageTracker.map_phase_to_stage('unknown'))
