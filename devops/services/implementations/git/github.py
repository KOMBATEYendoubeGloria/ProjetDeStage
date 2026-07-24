from .base import BaseGitService


class GitHubService(BaseGitService):
    """GitHub provider implementation."""

    provider_name = 'github'

    def __init__(self, token: str | None = None) -> None:
        super().__init__(token=token)
        self.repository_type = 'GitHub'
