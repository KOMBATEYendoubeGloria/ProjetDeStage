"""Serializer for artifact generation requests."""

from __future__ import annotations

from rest_framework import serializers


class ArtifactGenerationSerializer(serializers.Serializer):
    """Input serializer for all artifact generation endpoints.

    Every generator expects at least ``name`` and ``framework``.
    Additional fields are optional and forwarded to the engine as-is.
    """

    name = serializers.CharField(max_length=200, help_text='Project name.')
    type = serializers.CharField(max_length=100, required=False)
    framework = serializers.CharField(max_length=100, help_text='Application framework.')
    language = serializers.CharField(max_length=50, required=False)
    version = serializers.CharField(max_length=50, required=False)
    ports = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=65535),
        required=False,
        help_text='Exposed ports.',
    )
    environment = serializers.ChoiceField(
        choices=[
            ('dev', 'Development'),
            ('staging', 'Staging'),
            ('prod', 'Production'),
        ],
        required=False,
    )
    docker_image = serializers.CharField(max_length=200, required=False)
    database = serializers.CharField(max_length=50, required=False)
    redis = serializers.BooleanField(required=False)
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
    terraform = serializers.DictField(required=False)
    ansible = serializers.DictField(required=False)
    ci = serializers.DictField(required=False)

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Project name cannot be blank.')
        return value.strip()
