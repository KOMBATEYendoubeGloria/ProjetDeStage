from .base import BaseGitService


class GitLabService(BaseGitService):
    """GitLab provider implementation."""

    provider_name = 'gitlab'

    def __init__(self, token: str | None = None) -> None:
        super().__init__(token=token)
        self.repository_type = 'GitLab'
