import subprocess
from unittest.mock import patch

from django.test import SimpleTestCase

from devops.services.implementations.git.base import BaseGitService
from devops.services.implementations.git.github import GitHubService
from devops.exceptions import GitException


class GitServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = BaseGitService()

    @patch('devops.services.implementations.git.base.subprocess.run')
    def test_clone_calls_git(self, run_mock):
        run_mock.return_value.stdout = ''
        run_mock.return_value.returncode = 0
        self.service.clone('https://example.com/repo.git', '/tmp/repo', depth=1)
        run_mock.assert_called_once()

    @patch('devops.services.implementations.git.base.subprocess.run')
    def test_pull_calls_git(self, run_mock):
        run_mock.return_value.stdout = ''
        run_mock.return_value.returncode = 0
        self.service.pull('/tmp/repo', branch='main')
        run_mock.assert_called_once()

    @patch('devops.services.implementations.git.base.subprocess.run')
    def test_list_branches_parses_output(self, run_mock):
        run_mock.return_value.stdout = 'main\nfeature/test\n'
        run_mock.return_value.returncode = 0
        branches = self.service.list_branches('/tmp/repo', remote=False)
        self.assertEqual(branches, ['main', 'feature/test'])

    @patch('devops.services.implementations.git.base.subprocess.run')
    def test_get_status_parses_output(self, run_mock):
        run_mock.return_value.stdout = ' M file.py\n'
        run_mock.return_value.returncode = 0
        status = self.service.get_status('/tmp/repo')
        self.assertIn('raw', status)
        self.assertEqual(status['lines'], ['M file.py'])

    @patch('devops.services.implementations.git.base.subprocess.run')
    def test_git_exception_is_raised(self, run_mock):
        error = subprocess.CalledProcessError(1, ['git', 'status'], stderr=b'error')
        run_mock.side_effect = error
        with self.assertRaises(GitException):
            self.service.get_status('/tmp/repo')

    def test_github_service_is_instantiable(self):
        service = GitHubService()
        self.assertEqual(service.provider_name, 'github')
