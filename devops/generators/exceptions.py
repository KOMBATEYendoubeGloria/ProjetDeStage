"""Domain exception classes for the DevOps Artifact Generator Engine."""

from __future__ import annotations


class DevOpsGeneratorError(Exception):
    """Base exception for all DevOps generator errors."""

    pass


class ArtifactGenerationError(DevOpsGeneratorError):
    """Raised when artifact generation fails."""

    pass


class ArtifactValidationError(DevOpsGeneratorError):
    """Raised when project metadata validation fails."""

    pass


class TemplateNotFoundError(DevOpsGeneratorError):
    """Raised when a requested template file cannot be found."""

    pass


class ProjectAnalysisError(DevOpsGeneratorError):
    """Raised when project technology auto-detection fails."""

    pass
