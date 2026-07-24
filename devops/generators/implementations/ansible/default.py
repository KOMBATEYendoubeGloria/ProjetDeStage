"""Default Ansible artifact generator implementation."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from ...interfaces.ansible_generator import AnsibleGeneratorInterface
from ...validators.artifact_validator import ArtifactValidator
from ...engine.template_loader import TemplateLoader
from ...engine.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class DefaultAnsibleGenerator(AnsibleGeneratorInterface):
    """Generate Ansible playbook and inventory content from a project definition."""

    artifact_type = 'ansible'

    def __init__(self) -> None:
        self.validator = ArtifactValidator()
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()

    def generate(self, project: Mapping[str, Any]) -> str:
        return self.generate_ansible(project)

    def generate_ansible(self, project: Mapping[str, Any]) -> str:
        self.validator.validate(project)
        name = project['name']
        logger.info('Generating Ansible playbook for %s', name)
        port = project.get('ports', [8000])[0]
        context = {
            'name': name,
            'docker_image': project.get('docker_image', f'{name}:latest'),
            'port': port,
            'environment': project.get('environment', 'dev'),
        }
        try:
            template = self.loader.load('ansible/playbook.yml.j2')
            return self.renderer.render(template, context)
        except Exception:
            logger.warning('Ansible playbook template not found, using fallback')
            return (
                f"---\n- name: Deploy {name}\n  hosts: app_servers\n  become: true\n  tasks: []\n"
            )

    def generate_inventory(self, project: Mapping[str, Any]) -> str:
        hosts = project.get('ansible', {}).get('hosts', ['localhost']) if isinstance(project.get('ansible'), dict) else ['localhost']
        try:
            template = self.loader.load('ansible/inventory.ini.j2')
            return self.renderer.render(template, {})
        except Exception:
            logger.warning('Ansible inventory template not found, using fallback')
            lines = ['[app_servers]'] + [str(h) for h in hosts]
            return '\n'.join(lines) + '\n'
