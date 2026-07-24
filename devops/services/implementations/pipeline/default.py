from .base import BasePipelineService


class DefaultPipelineService(BasePipelineService):
    """Default pipeline lifecycle implementation."""

    provider_name = 'default'

    def __init__(self) -> None:
        super().__init__()
