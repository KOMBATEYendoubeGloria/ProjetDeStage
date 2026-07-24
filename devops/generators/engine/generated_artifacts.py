"""Data structure encapsulating generated DevOps artifacts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class GeneratedArtifacts:
    """Structured collection of generated DevOps deployment artifacts."""

    dockerfile: str = ''
    docker_compose: str = ''
    environment: str = ''
    terraform: str = ''
    ansible_playbook: str = ''
    ansible_inventory: str = ''
    pipeline: str = ''
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the generated artifacts object into a plain dictionary."""
        return asdict(self)

    def save_to_directory(self, output_dir: str | Path) -> Dict[str, str]:
        """Write all non-empty generated artifacts to the target output directory."""
        target_path = Path(output_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        saved_files: Dict[str, str] = {}

        file_mappings = {
            'dockerfile': 'Dockerfile',
            'docker_compose': 'docker-compose.yml',
            'environment': '.env',
            'terraform': 'main.tf',
            'ansible_playbook': 'playbook.yml',
            'ansible_inventory': 'inventory.ini',
        }

        # Pipeline file naming based on metadata or default
        ci_platform = self.metadata.get('ci_platform', 'github-actions')
        if ci_platform == 'jenkins':
            file_mappings['pipeline'] = 'Jenkinsfile'
        elif ci_platform == 'gitlab-ci':
            file_mappings['pipeline'] = '.gitlab-ci.yml'
        else:
            file_mappings['pipeline'] = '.github/workflows/deploy.yml'

        for attr, filename in file_mappings.items():
            content = getattr(self, attr, '')
            if content:
                file_path = target_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
                saved_files[attr] = str(file_path)

        # Write metadata.json
        meta_path = target_path / 'metadata.json'
        meta_path.write_text(json.dumps(self.metadata, indent=2), encoding='utf-8')
        saved_files['metadata'] = str(meta_path)

        return saved_files
