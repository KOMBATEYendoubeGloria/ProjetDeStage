"""Channel group naming conventions.

Groups map to logical broadcast targets:
- deployment:<id>  — all clients watching a specific deployment
- project:<id>     — all clients watching a project's deployments
- user:<id>        — all connections for a specific user
"""

from __future__ import annotations


def deployment_group_name(deployment_id: str) -> str:
    """Return the channel layer group name for a deployment."""
    return f'deployment:{deployment_id}'


def project_group_name(project_id: str) -> str:
    """Return the channel layer group name for a project."""
    return f'project:{project_id}'


def user_group_name(user_id: int) -> str:
    """Return the channel layer group name for a user."""
    return f'user:{user_id}'
