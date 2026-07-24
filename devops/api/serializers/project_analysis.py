"""Serializer for project analysis requests."""

from __future__ import annotations

from rest_framework import serializers


class ProjectAnalysisSerializer(serializers.Serializer):
    """Input serializer for the project analysis endpoint.

    Accepts either a ``name`` + optional metadata fields,
    or a ``path`` to a project directory on the server.
    """

    name = serializers.CharField(
        max_length=200,
        required=False,
        help_text='Project name.',
    )
    path = serializers.CharField(
        max_length=500,
        required=False,
        help_text='Absolute path to a project directory for auto-detection.',
    )
    framework = serializers.ChoiceField(
        choices=[
            ('django', 'Django'),
            ('nodejs', 'Node.js'),
            ('react', 'React'),
            ('laravel', 'Laravel'),
            ('springboot', 'Spring Boot'),
            ('generic', 'Generic'),
        ],
        required=False,
        help_text='Explicitly override the framework detection.',
    )
    language = serializers.CharField(max_length=50, required=False)
    version = serializers.CharField(max_length=50, required=False)
    ports = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=65535),
        required=False,
        help_text='List of ports the application exposes.',
    )
    database = serializers.CharField(max_length=50, required=False)
    provider = serializers.ChoiceField(
        choices=[
            ('docker', 'Docker'),
            ('proxmox', 'Proxmox'),
            ('vmware', 'VMware'),
            ('virtualbox', 'VirtualBox'),
        ],
        required=False,
    )
    ci_platform = serializers.ChoiceField(
        choices=[
            ('github-actions', 'GitHub Actions'),
            ('gitlab-ci', 'GitLab CI'),
            ('jenkins', 'Jenkins'),
        ],
        required=False,
    )
    environment = serializers.ChoiceField(
        choices=[
            ('dev', 'Development'),
            ('staging', 'Staging'),
            ('prod', 'Production'),
        ],
        required=False,
    )

    def validate(self, attrs):
        if not attrs.get('name') and not attrs.get('path'):
            raise serializers.ValidationError(
                'Either "name" or "path" must be provided.'
            )
        return attrs
