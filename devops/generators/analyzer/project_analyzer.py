"""Project technology and stack analyzer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Mapping

from .rules import (
    ALL_RULES,
    DetectionResult,
    DetectionRule,
)

logger = logging.getLogger(__name__)

# Files we always try to read when analysing a directory.
_IMPORTANT_FILES = {
    'requirements.txt', 'requirements-base.txt', 'requirements-dev.txt',
    'pyproject.toml', 'setup.py', 'Pipfile', 'Pipfile.lock',
    'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'composer.json', 'artisan',
    'pom.xml', 'build.gradle', 'build.gradle.kts',
    'go.mod', 'go.sum',
    'Cargo.toml', 'Cargo.lock',
    'Gemfile', 'Gemfile.lock',
    'manage.py', 'wsgi.py', 'asgi.py',
    'settings.py',
    'app.py', 'main.py', 'server.py', 'index.js', 'index.ts',
    'tsconfig.json',
    'next.config.js', 'next.config.mjs', 'next.config.ts',
    'vue.config.js', 'vue.config.ts',
    'angular.json', 'nest-cli.json',
    'vite.config.js', 'vite.config.ts', 'vite.config.mjs',
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    'docker-compose.dev.yml',
    'Program.cs',
}

_MAX_SCAN_DEPTH = 4
_CONTENT_MAX_BYTES = 64 * 1024  # 64 KB per file


class ProjectAnalyzer:
    """Auto-detects project framework, language, database dependencies, and default configurations."""

    FRAMEWORK_PORTS: Dict[str, list[int]] = {
        'django': [8000],
        'flask': [5000],
        'fastapi': [8000],
        'nodejs': [3000],
        'express': [3000],
        'nestjs': [3000],
        'react': [80],
        'nextjs': [3000],
        'vue': [3000],
        'angular': [4200],
        'vite': [5173],
        'laravel': [8000],
        'springboot': [8080],
        'go': [8080],
        'rust': [8080],
        'ruby': [3000],
        'dotnet': [5000],
        'generic': [8000],
    }

    FRAMEWORK_LANGUAGES: Dict[str, str] = {
        'django': 'python',
        'flask': 'python',
        'fastapi': 'python',
        'nodejs': 'javascript',
        'express': 'javascript',
        'nestjs': 'typescript',
        'react': 'javascript',
        'nextjs': 'typescript',
        'vue': 'javascript',
        'angular': 'typescript',
        'vite': 'javascript',
        'laravel': 'php',
        'springboot': 'java',
        'go': 'go',
        'rust': 'rust',
        'ruby': 'ruby',
        'dotnet': 'csharp',
        'generic': 'python',
    }

    def __init__(self, rules: list[DetectionRule] | None = None) -> None:
        self._rules = rules if rules is not None else [cls() for cls in ALL_RULES]

    # ------------------------------------------------------------------
    # Public API (unchanged signatures)
    # ------------------------------------------------------------------

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

        filenames, contents = self._collect_files(root)
        detections = self._run_rules(root, filenames, contents)
        return self._build_result(name, detections)

    def enrich_project_metadata(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Fill in missing fields in a project dictionary based on detected framework."""
        framework = project.get('framework') or project.get('type') or 'generic'
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
            enriched['database'] = self._default_database(framework)

        if 'provider' not in enriched:
            enriched['provider'] = 'docker'

        if 'ci_platform' not in enriched:
            enriched['ci_platform'] = 'github-actions'

        if 'environment' not in enriched:
            enriched['environment'] = 'dev'

        return enriched

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _collect_files(self, root: Path) -> tuple[set[str], Dict[str, str]]:
        """Walk the directory tree and read important files."""
        filenames: set[str] = set()
        contents: Dict[str, str] = {}

        for _depth, dirpath in _walk_with_depth(root, _MAX_SCAN_DEPTH):
            for entry in dirpath.iterdir():
                if entry.is_dir():
                    continue
                rel = entry.relative_to(root).as_posix()
                fname = entry.name
                filenames.add(rel)
                filenames.add(fname)

                if fname in _IMPORTANT_FILES or fname.endswith(('.py', '.js', '.ts', '.vue', '.jsx', '.tsx')):
                    if rel not in contents:
                        try:
                            data = entry.read_bytes()[:_CONTENT_MAX_BYTES]
                            contents[rel] = data.decode('utf-8', errors='replace')
                            contents[fname] = contents[rel]
                        except Exception:
                            pass

        return filenames, contents

    def _run_rules(
        self,
        root: Path,
        filenames: set[str],
        contents: Dict[str, str],
    ) -> list[DetectionResult]:
        """Execute all detection rules and return matches sorted by confidence."""
        results: list[DetectionResult] = []
        for rule in self._rules:
            try:
                result = rule.detect(root, filenames, contents)
                if result is not None:
                    result.category = rule.category
                    results.append(result)
            except Exception as exc:
                logger.debug('Rule %s failed: %s', rule.name, exc)

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results

    def _build_result(self, name: str, detections: list[DetectionResult]) -> Dict[str, Any]:
        """Construct the output dict from detection results."""
        frameworks = [
            d for d in detections if d.category == 'framework'
        ]
        languages = [
            d for d in detections if d.category == 'language'
        ]
        infra = [
            d for d in detections if d.category == 'infrastructure'
        ]

        primary_framework = frameworks[0] if frameworks else None
        primary_language = languages[0] if languages else primary_framework

        # Determine the primary technology name used by generators
        if primary_framework:
            framework_key = primary_framework.name
        elif primary_language:
            framework_key = primary_language.name
        elif detections:
            framework_key = detections[0].name
        else:
            framework_key = 'generic'

        # Merge default configs: primary framework wins
        merged_config: Dict[str, Any] = {}
        if primary_framework and primary_framework.default_config:
            merged_config.update(primary_framework.default_config)
        elif primary_language and primary_language.default_config:
            merged_config.update(primary_language.default_config)

        ports = merged_config.get('ports', self.FRAMEWORK_PORTS.get(framework_key, [8000]))
        language = merged_config.get('language', self.FRAMEWORK_LANGUAGES.get(framework_key, 'python'))
        database = merged_config.get('database', self._default_database(framework_key))
        version = merged_config.get('version', self._default_version(framework_key))

        # Collect all reasons
        all_reasons: list[str] = []
        for d in detections:
            all_reasons.extend(d.reasons)

        # Stack names
        stack = [d.name for d in detections if d.category in ('framework', 'language')]

        # Overall confidence: weighted by primary detection
        if detections:
            confidence = detections[0].confidence
        else:
            confidence = 0.0

        # Enrichment metadata for infrastructure
        has_docker = any(d.name == 'docker' for d in infra)

        result = {
            'name': name,
            'type': framework_key,
            'framework': framework_key,
            'language': language,
            'version': version,
            'ports': ports,
            'database': database,
            'redis': True,
            'provider': 'docker',
            'ci_platform': 'github-actions',
            'environment': 'dev',

            # Extended detection fields
            'primary_language': language,
            'primary_framework': framework_key,
            'secondary_frameworks': [
                d.name for d in frameworks[1:]
            ],
            'stack': stack,
            'confidence': confidence,
            'detection_reasons': all_reasons,
            'infra': [d.name for d in infra],
        }

        logger.info(
            'Detected %s (confidence %.0f%%) — stack: %s',
            framework_key,
            confidence * 100,
            ', '.join(stack) or 'unknown',
        )
        return result

    @staticmethod
    def _default_version(framework: str) -> str:
        defaults = {
            'django': '3.11',
            'flask': '3.11',
            'fastapi': '3.11',
            'nodejs': '18-alpine',
            'express': '18-alpine',
            'nestjs': '18-alpine',
            'react': '18-alpine',
            'nextjs': '18-alpine',
            'vue': '18-alpine',
            'angular': '18-alpine',
            'vite': '18-alpine',
            'laravel': '8.2',
            'springboot': '17-jdk-slim',
            'go': '1.21-alpine',
            'rust': '1.75-slim',
            'ruby': '3.2-slim',
            'dotnet': '8.0-alpine',
            'generic': '3.11',
        }
        return defaults.get(framework, '3.11')

    @staticmethod
    def _default_database(framework: str) -> str:
        defaults = {
            'django': 'postgres',
            'flask': 'sqlite',
            'fastapi': 'postgres',
            'nodejs': 'mongodb',
            'express': 'mongodb',
            'nestjs': 'postgres',
            'react': 'mongodb',
            'nextjs': 'mongodb',
            'vue': 'mongodb',
            'angular': 'mongodb',
            'vite': 'mongodb',
            'laravel': 'mysql',
            'springboot': 'postgres',
            'go': 'postgres',
            'rust': 'postgres',
            'ruby': 'postgres',
            'dotnet': 'postgres',
            'generic': 'postgres',
        }
        return defaults.get(framework, 'postgres')


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _walk_with_depth(root: Path, max_depth: int):
    """Yield (depth, dirpath) tuples up to *max_depth*."""
    yield (0, root)
    if max_depth <= 0:
        return
    try:
        for child in sorted(root.iterdir()):
            if child.is_dir() and not child.name.startswith('.') and child.name not in {
                'node_modules', '__pycache__', 'venv', '.venv', 'vendor',
                '.git', '.tox', '.mypy_cache', '.pytest_cache',
            }:
                yield from _walk_with_depth(child, max_depth - 1)
    except PermissionError:
        pass
