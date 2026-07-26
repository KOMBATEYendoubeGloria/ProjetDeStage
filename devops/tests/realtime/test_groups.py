"""Tests for channel group naming helpers."""

from django.test import SimpleTestCase

from devops.realtime.groups import (
    deployment_group_name,
    project_group_name,
    user_group_name,
)


class GroupNameTests(SimpleTestCase):

    def test_deployment_group(self):
        self.assertEqual(deployment_group_name('abc-123'), 'deployment:abc-123')

    def test_project_group(self):
        self.assertEqual(project_group_name('proj-456'), 'project:proj-456')

    def test_user_group(self):
        self.assertEqual(user_group_name(42), 'user:42')

    def test_deployment_group_prefix(self):
        result = deployment_group_name('x')
        self.assertTrue(result.startswith('deployment:'))

    def test_project_group_prefix(self):
        result = project_group_name('x')
        self.assertTrue(result.startswith('project:'))

    def test_user_group_prefix(self):
        result = user_group_name(1)
        self.assertTrue(result.startswith('user:'))
