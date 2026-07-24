"""Serializer for provider configuration requests."""

from __future__ import annotations

from rest_framework import serializers


class ProviderSerializer(serializers.Serializer):
    """Input serializer for provider-related operations."""

    provider = serializers.ChoiceField(
        choices=[
            ('docker', 'Docker'),
            ('proxmox', 'Proxmox'),
            ('vmware', 'VMware'),
            ('virtualbox', 'VirtualBox'),
        ],
        help_text='Infrastructure provider.',
    )
    config = serializers.DictField(
        required=False,
        help_text='Provider-specific configuration overrides.',
    )
