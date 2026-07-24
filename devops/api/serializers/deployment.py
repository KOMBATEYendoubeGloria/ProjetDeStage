"""Serializer for deployment-related requests."""

from __future__ import annotations

from rest_framework import serializers


class DeploymentSerializer(serializers.Serializer):
    """Input serializer for deployment requests."""

    project_id = serializers.IntegerField(help_text='ProjetApplicatif ID.')
    environment = serializers.ChoiceField(
        choices=[
            ('dev', 'Development'),
            ('staging', 'Staging'),
            ('prod', 'Production'),
        ],
    )
    target = serializers.CharField(max_length=200, required=False)
    commit_hash = serializers.CharField(max_length=40, required=False)
    metadata = serializers.DictField(required=False)
