"""Remote artifact transfer — copies local workspace files to a remote host via SSH."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, List

logger = logging.getLogger(__name__)


def transfer_artifacts(
    ssh_service: Any,
    local_workspace: str,
    remote_workspace: str,
    filenames: List[str],
) -> None:
    """Copy specific files from ``local_workspace`` to ``remote_workspace`` on the remote host.

    ``ssh_service`` must be a connected ``BaseSSHService`` instance.
    """
    remote_mkdir_cmd = f'mkdir -p {remote_workspace}'
    ssh_service.execute(remote_mkdir_cmd)
    logger.info('Created remote workspace: %s', remote_workspace)

    for filename in filenames:
        local_path = os.path.join(local_workspace, filename)
        if not os.path.exists(local_path):
            logger.warning('Local artifact not found, skipping: %s', local_path)
            continue
        remote_path = f'{remote_workspace}/{filename}'
        ssh_service.copy(local_path, remote_path)
        logger.info('Transferred %s -> %s', local_path, remote_path)


def transfer_workspace(
    ssh_service: Any,
    local_workspace: str,
    remote_workspace: str,
) -> None:
    """Copy all files in ``local_workspace`` to ``remote_workspace``."""
    local_dir = Path(local_workspace)
    if not local_dir.is_dir():
        logger.warning('Local workspace does not exist: %s', local_workspace)
        return

    filenames = [f.name for f in local_dir.iterdir() if f.is_file()]
    if filenames:
        transfer_artifacts(ssh_service, local_workspace, remote_workspace, filenames)
