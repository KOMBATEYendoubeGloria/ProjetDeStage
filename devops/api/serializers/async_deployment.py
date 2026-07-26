"""Serializers for asynchronous deployment monitoring."""

from __future__ import annotations

from rest_framework import serializers


class AsyncDeploymentStartSerializer(serializers.Serializer):
    """Input serializer for starting an async deployment."""

    provider_name = serializers.CharField(max_length=50)
    project = serializers.DictField()
    artifacts = serializers.DictField()
    config = serializers.DictField(required=False, default=dict)


class DeploymentStatusSerializer(serializers.Serializer):
    """Output serializer for deployment job status."""

    deployment_id = serializers.UUIDField()
    phase = serializers.CharField()
    status = serializers.CharField()
    progress_percent = serializers.IntegerField()
    stages = serializers.ListField(child=serializers.DictField(), required=False)
    started_at = serializers.CharField(allow_null=True)
    finished_at = serializers.CharField(allow_null=True)
    error_message = serializers.CharField(allow_blank=True)


class DeploymentLogSerializer(serializers.Serializer):
    """Output serializer for deployment log entries."""

    timestamp = serializers.CharField()
    level = serializers.CharField()
    message = serializers.CharField()
    stage = serializers.CharField()


class DeploymentEventSerializer(serializers.Serializer):
    """Output serializer for deployment events."""

    event_type = serializers.CharField()
    payload = serializers.DictField()
    created_at = serializers.CharField()
