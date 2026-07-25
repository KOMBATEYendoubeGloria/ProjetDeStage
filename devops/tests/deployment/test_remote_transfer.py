"""Tests for remote artifact transfer — all SSH calls mocked."""

import os
import tempfile

from unittest.mock import MagicMock, call, patch

from django.test import SimpleTestCase

from devops.deployment.remote.transfer import transfer_artifacts, transfer_workspace


class TransferArtifactsTests(SimpleTestCase):

    @patch('devops.deployment.remote.transfer.os.path.exists', return_value=True)
    def test_creates_remote_dir_and_copies(self, mock_exists):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        mock_ssh.copy.return_value = None
        transfer_artifacts(mock_ssh, '/local', '/remote', ['main.tf', 'Dockerfile'])
        mock_ssh.execute.assert_called_once_with('mkdir -p /remote')
        self.assertEqual(mock_ssh.copy.call_count, 2)

    @patch('devops.deployment.remote.transfer.os.path.exists', return_value=False)
    def test_skips_missing_files(self, mock_exists):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        transfer_artifacts(mock_ssh, '/local', '/remote', ['missing.tf'])
        mock_ssh.copy.assert_not_called()

    def test_empty_filenames_creates_dir_only(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        transfer_artifacts(mock_ssh, '/local', '/remote', [])
        mock_ssh.execute.assert_called_once_with('mkdir -p /remote')
        mock_ssh.copy.assert_not_called()


class TransferWorkspaceTests(SimpleTestCase):

    def test_transfers_all_files(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {'stdout': '', 'stderr': '', 'exit_code': 0}
        mock_ssh.copy.return_value = None
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ['a.tf', 'b.yml']:
                open(os.path.join(tmpdir, name), 'w').close()
            transfer_workspace(mock_ssh, tmpdir, '/remote')
            self.assertEqual(mock_ssh.copy.call_count, 2)

    def test_nonexistent_workspace(self):
        mock_ssh = MagicMock()
        transfer_workspace(mock_ssh, '/nonexistent/path', '/remote')
        mock_ssh.execute.assert_not_called()

    def test_empty_workspace(self):
        mock_ssh = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            transfer_workspace(mock_ssh, tmpdir, '/remote')
            mock_ssh.copy.assert_not_called()
