"""Project technology and stack analyzer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Mapping

logger = logging.getLogger(__name__)


class ProjectAnalyzer:
    """Auto-detects project framework, language, database dependencies, and default configurations."""

    FRAMEWORK_PORTS = {
        'django': [8000],
        'nodejs': [3000],
        'react': [80],
        'laravel': [8000],
        'springboot': [8080],
        'generic': [8000],
    }

    FRAMEWORK_LANGUAGES = {
        'django': 'python',
        'nodejs': 'javascript',
        'react': 'javascript',
        'laravel': 'php',
        'springboot': 'java',
        'generic': 'python',
    }

    def analyze(self, project_or_path: Mapping[str, Any] | str | Path) -> Dict[str, Any]:
        """Analyze project input (either a metadata dict or a file system path)."""
        if isinstance(project_or_path, (str, Path)):
            return self.analyze_directory(Path(project_or_path))
        
        project_dict = dict(project_or_path)
        return self.enrich_project_metadata(project_dict)

    def analyze_directory(self, root_path: Path) -> Dict[str, Any]:
        """Inspect directory markers to determine project stack."""
        root = Path(root_path)
        name = root.name or 'sample-app'

        framework = 'generic'
        language = 'python'
        database = 'postgres'
        ports = [8000]

        if (root / 'manage.py').exists() or (root / 'requirements.txt').exists() or (root / 'pyproject.toml').exists():
            framework = 'django'
            language = 'python'
            database = 'postgres'
        elif (root / 'package.json').exists():
            pkg_content = ''
            try:
                pkg_content = (root / 'package.json').read_text(encoding='utf-8').lower()
            except Exception:
                pass
            
            if 'react' in pkg_content:
                framework = 'react'
                ports = [80]
            else:
                framework = 'nodejs'
                ports = [3000]
            language = 'typescript' if (root / 'tsconfig.json').exists() else 'javascript'
            database = 'mongodb'
        elif (root / 'composer.json').exists() or (root / 'artisan').exists():
            framework = 'laravel'
            language = 'php'
            database = 'mysql'
            ports = [8000]
        elif (root / 'pom.xml').exists() or (root / 'build.gradle').exists():
            framework = 'springboot'
            language = 'java'
            database = 'postgres'
            ports = [8080]

        return {
            'name': name,
            'type': framework,
            'framework': framework,
            'language': language,
            'version': self._default_version(framework),
            'ports': ports,
            'database': database,
            'redis': True,
            'provider': 'docker',
            'ci_platform': 'github-actions',
            'environment': 'dev',
        }

    def enrich_project_metadata(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Fill in missing fields in a project dictionary based on detected framework."""
        framework = project.get('framework') or project.get('type') or 'django'
        framework = framework.lower()

        enriched = dict(project)
        enriched['framework'] = framework
        enriched['name'] = project.get('name', 'app')
        enriched['type'] = framework

        if 'language' not in enriched:
            enriched['language'] = self.FRAMEWORK_LANGUAGES.get(framework, 'python')

        if 'ports' not in enriched or not isinstance(enriched['ports'], list):
            enriched['ports'] = self.FRAMEWORK_PORTS.get(framework, [8000])

        if 'version' not in enriched:
            enriched['version'] = self._default_version(framework)

        if 'database' not in enriched:
            enriched['database'] = 'postgres' if framework in ('django', 'springboot') else ('mysql' if framework == 'laravel' else 'mongodb')

        if 'provider' not in enriched:
            enriched['provider'] = 'docker'

        if 'ci_platform' not in enriched:
            enriched['ci_platform'] = 'github-actions'

        if 'environment' not in enriched:
            enriched['environment'] = 'dev'

        return enriched

    def _default_version(self, framework: str) -> str:
        defaults = {
            'django': '3.11',
            'nodejs': '18-alpine',
            'react': '18-alpine',
            'laravel': '8.2',
            'springboot': '17-jdk-slim',
            'generic': '3.11',
        }
        return defaults.get(framework, '3.11')
