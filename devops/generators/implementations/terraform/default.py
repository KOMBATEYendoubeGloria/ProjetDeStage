"""Default Terraform artifact generator implementation."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from ...interfaces.terraform_generator import TerraformGeneratorInterface
from ...validators.artifact_validator import ArtifactValidator
from ...engine.template_loader import TemplateLoader
from ...engine.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class DefaultTerraformGenerator(TerraformGeneratorInterface):
    """Generate Terraform manifests from a project definition."""

    artifact_type = 'terraform'

    def __init__(self) -> None:
        self.validator = ArtifactValidator()
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()

    def generate(self, project: Mapping[str, Any]) -> str:
        return self.generate_terraform(project)

    def generate_terraform(self, project: Mapping[str, Any]) -> str:
        self.validator.validate(project)
        name = project['name']
        provider = project.get('provider', 'docker')
        logger.info('Generating Terraform (%s) for %s', provider, name)
        port = project.get('ports', [8000])[0]
        context = {
            'name': name,
            'provider': provider,
            'docker_image': project.get('docker_image', f'{name}:latest'),
            'port': port,
            'cpu': project.get('cpu', 2),
            'memory_mb': project.get('memory_mb', 2048),
            'disk_gb': project.get('disk_gb', 20),
            'proxmox_endpoint': project.get('proxmox_endpoint', 'https://proxmox.local:8006/api2/json'),
            'vmware_server': project.get('vmware_server', 'vsphere.local'),
        }
        template_map = {
            'proxmox': 'terraform/proxmox/main.tf.j2',
            'vmware': 'terraform/vmware/main.tf.j2',
            'virtualbox': 'terraform/virtualbox/main.tf.j2',
            'docker': 'terraform/docker/main.tf.j2',
        }
        template_name = template_map.get(provider, 'terraform/docker/main.tf.j2')
        try:
            template = self.loader.load(template_name)
            return self.renderer.render(template, context)
        except Exception:
            logger.warning('Template %s not found, using fallback for terraform', template_name)
            return (
                f"# terraform configuration for {name}\n"
                f"terraform {{\n  required_version = \">= 1.0\"\n}}\n"
                f"# provider: {provider}\n"
            )
