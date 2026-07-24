"""Serializer for GenerationHistory model."""

from __future__ import annotations

from rest_framework import serializers

from devops.models import GenerationHistory


class GenerationHistorySerializer(serializers.ModelSerializer):
    """Read-only serializer for generation history audit records."""

    class Meta:
        model = GenerationHistory
        fields = [
            'id',
            'project_name',
            'framework',
            'provider',
            'ci_platform',
            'artifacts_generated',
            'status',
            'created_at',
        ]
        read_only_fields = fields
