"""Technology detection rules — each rule recognises one technology."""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Shared data structures
# ---------------------------------------------------------------------------

@dataclass
class DetectionResult:
    """Result produced by a single detection rule."""

    name: str
    confidence: float
    reasons: List[str]
    default_config: Dict[str, Any] = field(default_factory=dict)
    category: str = 'framework'


class DetectionRule(ABC):
    """Base class for all technology detection rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def category(self) -> str:
        """One of 'language', 'framework', 'infrastructure'."""
        ...

    @abstractmethod
    def detect(
        self,
        root: Path,
        filenames: set[str],
        contents: Dict[str, str],
    ) -> Optional[DetectionResult]:
        ...


# ---------------------------------------------------------------------------
# Python ecosystem
# ---------------------------------------------------------------------------

class DjangoRule(DetectionRule):
    name = 'django'
    category = 'framework'

    def detect(self, root, filenames, contents):
        score = 0.0
        reasons: list[str] = []

        # Strong marker: manage.py referencing Django
        if 'manage.py' in filenames:
            txt = contents.get('manage.py', '')
            if 'DJANGO_SETTINGS_MODULE' in txt or 'django' in txt.lower():
                score += 0.45
                reasons.append('manage.py references Django')

        # requirements files mentioning django
        for req in ('requirements.txt', 'requirements-base.txt', 'requirements-dev.txt'):
            if req in filenames:
                txt = contents.get(req, '').lower()
                if 'django' in txt:
                    score += 0.25
                    reasons.append(f'{req} contains django')
                    break

        # pyproject.toml mentioning django
        if 'pyproject.toml' in filenames:
            txt = contents.get('pyproject.toml', '').lower()
            if 'django' in txt:
                score += 0.20
                reasons.append('pyproject.toml contains django')

        # setup.py mentioning django
        if 'setup.py' in filenames:
            txt = contents.get('setup.py', '').lower()
            if 'django' in txt:
                score += 0.15
                reasons.append('setup.py contains django')

        # settings.py with Django-specific patterns
        if 'settings.py' in filenames:
            txt = contents.get('settings.py', '')
            if 'INSTALLED_APPS' in txt or 'MIDDLEWARE' in txt:
                score += 0.15
                reasons.append('settings.py contains Django configuration patterns')

        # wsgi.py or asgi.py referencing Django
        for entry in ('wsgi.py', 'asgi.py'):
            if entry in filenames:
                txt = contents.get(entry, '').lower()
                if 'django' in txt or 'get_wsgi_application' in txt or 'get_asgi_application' in txt:
                    score += 0.10
                    reasons.append(f'{entry} references Django')

        if score < 0.20:
            return None

        return DetectionResult(
            name='django',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'python',
                'ports': [8000],
                'database': 'postgres',
                'version': '3.11',
            },
        )


class FlaskRule(DetectionRule):
    name = 'flask'
    category = 'framework'

    def detect(self, root, filenames, contents):
        score = 0.0
        reasons: list[str] = []

        for req in ('requirements.txt', 'requirements-base.txt', 'requirements-dev.txt', 'Pipfile', 'pyproject.toml'):
            if req in filenames:
                txt = contents.get(req, '').lower()
                if re.search(r'\bflask\b', txt):
                    score += 0.35
                    reasons.append(f'{req} contains flask')
                    break

        if 'setup.py' in filenames:
            txt = contents.get('setup.py', '').lower()
            if 'flask' in txt:
                score += 0.20
                reasons.append('setup.py contains flask')

        # Scan common entry points for Flask imports
        for fname in ('app.py', 'main.py', 'wsgi.py', 'server.py'):
            if fname in filenames:
                txt = contents.get(fname, '')
                if re.search(r'from\s+flask\s+import|Flask\(__name__\)', txt):
                    score += 0.35
                    reasons.append(f'{fname} contains Flask import')
                    break

        # Recursive scan for Flask imports in *.py files (limited set)
        if score < 0.30:
            for fname, txt in contents.items():
                if fname.endswith('.py') and re.search(r'from\s+flask\s+import', txt):
                    score += 0.15
                    reasons.append(f'{fname} imports Flask')
                    break

        if score < 0.20:
            return None

        return DetectionResult(
            name='flask',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'python',
                'ports': [5000],
                'database': 'sqlite',
                'version': '3.11',
            },
        )


class FastAPIRule(DetectionRule):
    name = 'fastapi'
    category = 'framework'

    def detect(self, root, filenames, contents):
        score = 0.0
        reasons: list[str] = []

        for req in ('requirements.txt', 'requirements-base.txt', 'requirements-dev.txt', 'Pipfile', 'pyproject.toml'):
            if req in filenames:
                txt = contents.get(req, '').lower()
                if 'fastapi' in txt:
                    score += 0.35
                    reasons.append(f'{req} contains fastapi')
                    break

        if 'setup.py' in filenames:
            txt = contents.get('setup.py', '').lower()
            if 'fastapi' in txt:
                score += 0.20
                reasons.append('setup.py contains fastapi')

        for fname in ('main.py', 'app.py', 'server.py'):
            if fname in filenames:
                txt = contents.get(fname, '')
                if re.search(r'from\s+fastapi\s+import|FastAPI\(', txt):
                    score += 0.40
                    reasons.append(f'{fname} contains FastAPI import')
                    break

        if score < 0.20:
            return None

        return DetectionResult(
            name='fastapi',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'python',
                'ports': [8000],
                'database': 'postgres',
                'version': '3.11',
            },
        )


# ---------------------------------------------------------------------------
# Node.js ecosystem
# ---------------------------------------------------------------------------

def _parse_package_json(root: Path, filenames: set[str], contents: Dict[str, str]) -> Optional[dict]:
    if 'package.json' not in filenames:
        return None
    raw = contents.get('package.json', '')
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None


class ExpressRule(DetectionRule):
    name = 'express'
    category = 'framework'

    def detect(self, root, filenames, contents):
        pkg = _parse_package_json(root, filenames, contents)
        if pkg is None:
            return None

        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        reasons: list[str] = []

        if 'express' in deps:
            reasons.append('express found in package.json dependencies')
        else:
            return None

        score = 0.60

        # Check for express usage in code
        for fname in ('app.js', 'server.js', 'index.js', 'src/app.js', 'src/server.js'):
            if fname in filenames:
                txt = contents.get(fname, '')
                if re.search(r"require\(['\"]express['\"]\)|from\s+['\"]express['\"]", txt):
                    score += 0.30
                    reasons.append(f'{fname} imports express')
                    break

        return DetectionResult(
            name='express',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'javascript',
                'ports': [3000],
                'database': 'mongodb',
                'version': '18-alpine',
            },
        )


class NestJSRule(DetectionRule):
    name = 'nestjs'
    category = 'framework'

    def detect(self, root, filenames, contents):
        pkg = _parse_package_json(root, filenames, contents)
        if pkg is None:
            return None

        all_deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        reasons: list[str] = []

        if '@nestjs/core' in all_deps:
            reasons.append('@nestjs/core found in package.json')
        elif '@nestjs/common' in all_deps:
            reasons.append('@nestjs/common found in package.json')
        else:
            return None

        score = 0.85

        if 'nest-cli.json' in filenames:
            score += 0.10
            reasons.append('nest-cli.json found')

        return DetectionResult(
            name='nestjs',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'typescript',
                'ports': [3000],
                'database': 'postgres',
                'version': '18-alpine',
            },
        )


class ReactRule(DetectionRule):
    name = 'react'
    category = 'framework'

    def detect(self, root, filenames, contents):
        pkg = _parse_package_json(root, filenames, contents)
        if pkg is None:
            return None

        deps = pkg.get('dependencies', {})
        reasons: list[str] = []

        has_react = 'react' in deps and 'react-dom' in deps
        if not has_react:
            return None

        reasons.append('react and react-dom found in dependencies')
        score = 0.70

        # Stronger signal: CRA or React-specific config
        if any(f in filenames for f in ('craco.config.js', '.babelrc', 'babel.config.js')):
            score += 0.05

        if pkg.get('scripts', {}).get('start'):
            score += 0.05
            reasons.append('package.json has start script')

        return DetectionResult(
            name='react',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'javascript',
                'ports': [80],
                'database': 'mongodb',
                'version': '18-alpine',
            },
        )


class NextJSRule(DetectionRule):
    name = 'nextjs'
    category = 'framework'

    def detect(self, root, filenames, contents):
        pkg = _parse_package_json(root, filenames, contents)
        if pkg is None:
            return None

        all_deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        reasons: list[str] = []

        if 'next' not in all_deps:
            return None

        reasons.append('next found in package.json dependencies')
        score = 0.80

        if any(f in filenames for f in ('next.config.js', 'next.config.mjs', 'next.config.ts')):
            score += 0.15
            reasons.append('next.config file found')

        return DetectionResult(
            name='nextjs',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'typescript',
                'ports': [3000],
                'database': 'mongodb',
                'version': '18-alpine',
            },
        )


class VueRule(DetectionRule):
    name = 'vue'
    category = 'framework'

    def detect(self, root, filenames, contents):
        pkg = _parse_package_json(root, filenames, contents)
        if pkg is None:
            return None

        deps = pkg.get('dependencies', {})
        reasons: list[str] = []

        if 'vue' not in deps:
            return None

        reasons.append('vue found in package.json dependencies')
        score = 0.65

        if 'vue.config.js' in filenames or 'vue.config.ts' in filenames:
            score += 0.15
            reasons.append('vue.config file found')
        elif any(f in filenames for f in ('vite.config.js', 'vite.config.ts')):
            score += 0.10
            reasons.append('vite config found (Vue likely uses Vite)')

        return DetectionResult(
            name='vue',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'javascript',
                'ports': [3000],
                'database': 'mongodb',
                'version': '18-alpine',
            },
        )


class AngularRule(DetectionRule):
    name = 'angular'
    category = 'framework'

    def detect(self, root, filenames, contents):
        pkg = _parse_package_json(root, filenames, contents)
        if pkg is None:
            return None

        all_deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        reasons: list[str] = []

        has_angular = '@angular/core' in all_deps
        if not has_angular:
            return None

        reasons.append('@angular/core found in package.json')
        score = 0.85

        if 'angular.json' in filenames:
            score += 0.10
            reasons.append('angular.json found')

        return DetectionResult(
            name='angular',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'typescript',
                'ports': [4200],
                'database': 'mongodb',
                'version': '18-alpine',
            },
        )


class ViteRule(DetectionRule):
    name = 'vite'
    category = 'framework'

    def detect(self, root, filenames, contents):
        pkg = _parse_package_json(root, filenames, contents)
        if pkg is None:
            return None

        dev_deps = pkg.get('devDependencies', {})
        reasons: list[str] = []

        if 'vite' not in dev_deps:
            return None

        reasons.append('vite found in devDependencies')
        score = 0.50

        if any(f in filenames for f in ('vite.config.js', 'vite.config.ts', 'vite.config.mjs')):
            score += 0.20
            reasons.append('vite config file found')

        return DetectionResult(
            name='vite',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'javascript',
                'ports': [5173],
                'database': 'mongodb',
                'version': '18-alpine',
            },
        )


# ---------------------------------------------------------------------------
# PHP ecosystem
# ---------------------------------------------------------------------------

class LaravelRule(DetectionRule):
    name = 'laravel'
    category = 'framework'

    def detect(self, root, filenames, contents):
        score = 0.0
        reasons: list[str] = []

        if 'artisan' in filenames:
            score += 0.30
            reasons.append('artisan file found')

        if 'composer.json' in filenames:
            txt = contents.get('composer.json', '').lower()
            if 'laravel/framework' in txt:
                score += 0.45
                reasons.append('laravel/framework found in composer.json')

        if score < 0.20:
            return None

        return DetectionResult(
            name='laravel',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'php',
                'ports': [8000],
                'database': 'mysql',
                'version': '8.2',
            },
        )


# ---------------------------------------------------------------------------
# Java ecosystem
# ---------------------------------------------------------------------------

class SpringBootRule(DetectionRule):
    name = 'springboot'
    category = 'framework'

    def detect(self, root, filenames, contents):
        score = 0.0
        reasons: list[str] = []

        if 'pom.xml' in filenames:
            txt = contents.get('pom.xml', '').lower()
            if 'spring-boot' in txt:
                score += 0.50
                reasons.append('spring-boot found in pom.xml')

        if 'build.gradle' in filenames or 'build.gradle.kts' in filenames:
            fname = 'build.gradle' if 'build.gradle' in filenames else 'build.gradle.kts'
            txt = contents.get(fname, '').lower()
            if 'org.springframework.boot' in txt or 'spring-boot' in txt:
                score += 0.50
                reasons.append(f'spring-boot found in {fname}')

        # Look for Java source directories
        if (root / 'src' / 'main' / 'java').exists():
            score += 0.05
            reasons.append('standard Java src directory structure found')

        if score < 0.20:
            return None

        return DetectionResult(
            name='springboot',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'java',
                'ports': [8080],
                'database': 'postgres',
                'version': '17-jdk-slim',
            },
        )


# ---------------------------------------------------------------------------
# Go ecosystem
# ---------------------------------------------------------------------------

class GoRule(DetectionRule):
    name = 'go'
    category = 'language'

    def detect(self, root, filenames, contents):
        if 'go.mod' not in filenames:
            return None

        reasons = ['go.mod found']
        score = 0.80

        txt = contents.get('go.mod', '')
        # Extract module name for context
        match = re.search(r'^module\s+(.+)$', txt, re.MULTILINE)
        if match:
            reasons.append(f'Go module: {match.group(1).strip()}')

        if (root / 'main.go').exists() or any(f.endswith('.go') for f in filenames if f != 'go.mod'):
            score += 0.10
            reasons.append('Go source files found')

        return DetectionResult(
            name='go',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'go',
                'ports': [8080],
                'database': 'postgres',
                'version': '1.21-alpine',
            },
        )


# ---------------------------------------------------------------------------
# Rust ecosystem
# ---------------------------------------------------------------------------

class RustRule(DetectionRule):
    name = 'rust'
    category = 'language'

    def detect(self, root, filenames, contents):
        if 'Cargo.toml' not in filenames:
            return None

        reasons = ['Cargo.toml found']
        score = 0.80

        txt = contents.get('Cargo.toml', '')
        if re.search(r'^name\s*=', txt, re.MULTILINE):
            score += 0.05
            reasons.append('Cargo.toml has package name')

        if any(f.endswith('.rs') for f in filenames):
            score += 0.10
            reasons.append('Rust source files found')

        return DetectionResult(
            name='rust',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'rust',
                'ports': [8080],
                'database': 'postgres',
                'version': '1.75-slim',
            },
        )


# ---------------------------------------------------------------------------
# Ruby ecosystem
# ---------------------------------------------------------------------------

class RubyRule(DetectionRule):
    name = 'ruby'
    category = 'language'

    def detect(self, root, filenames, contents):
        if 'Gemfile' not in filenames:
            return None

        reasons = ['Gemfile found']
        score = 0.65

        txt = contents.get('Gemfile', '').lower()
        if 'rails' in txt:
            score += 0.20
            reasons.append('Rails found in Gemfile')
        elif 'sinatra' in txt:
            score += 0.15
            reasons.append('Sinatra found in Gemfile')
        else:
            reasons.append('Ruby project detected from Gemfile')

        return DetectionResult(
            name='ruby',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'ruby',
                'ports': [3000],
                'database': 'postgres',
                'version': '3.2-slim',
            },
        )


# ---------------------------------------------------------------------------
# .NET ecosystem
# ---------------------------------------------------------------------------

class DotNetRule(DetectionRule):
    name = 'dotnet'
    category = 'language'

    def detect(self, root, filenames, contents):
        csproj_files = [f for f in filenames if f.endswith('.csproj')]
        if not csproj_files:
            return None

        reasons = [f'Found {len(csproj_files)} .csproj file(s)']
        score = 0.75

        if 'Program.cs' in filenames:
            score += 0.10
            reasons.append('Program.cs found')

        # Check for ASP.NET in csproj content
        for csproj in csproj_files:
            txt = contents.get(csproj, '').lower()
            if 'microsoft.aspnetcore' in txt:
                score += 0.10
                reasons.append(f'{csproj} references ASP.NET Core')
                break

        return DetectionResult(
            name='dotnet',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={
                'language': 'csharp',
                'ports': [5000],
                'database': 'postgres',
                'version': '8.0-alpine',
            },
        )


# ---------------------------------------------------------------------------
# Infrastructure detection (bonus — enriches, never replaces)
# ---------------------------------------------------------------------------

class DockerRule(DetectionRule):
    name = 'docker'
    category = 'infrastructure'

    def detect(self, root, filenames, contents):
        reasons: list[str] = []
        score = 0.0

        if 'Dockerfile' in filenames or any(f.startswith('Dockerfile.') for f in filenames):
            score += 0.50
            reasons.append('Dockerfile found')

        for f in ('docker-compose.yml', 'docker-compose.yaml', 'docker-compose.dev.yml'):
            if f in filenames:
                score += 0.40
                reasons.append(f'{f} found')
                break

        if score == 0:
            return None

        return DetectionResult(
            name='docker',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={},
        )


class KubernetesRule(DetectionRule):
    name = 'kubernetes'
    category = 'infrastructure'

    def detect(self, root, filenames, contents):
        reasons: list[str] = []
        score = 0.0

        if 'Dockerfile' in filenames:
            score += 0.30

        if any('k8s' in f.lower() or 'kubernetes' in f.lower() for f in filenames):
            score += 0.40
            reasons.append('Kubernetes manifest found')

        if any(f in filenames for f in ('helmfile.yaml', 'Chart.yaml')):
            score += 0.30
            reasons.append('Helm chart found')

        for f in ('.github/workflows/deploy.yml', '.github/workflows/deploy.yaml'):
            if f in filenames:
                score += 0.10
                reasons.append(f'{f} found')
                break

        if score < 0.20:
            return None

        return DetectionResult(
            name='kubernetes',
            confidence=min(round(score, 2), 1.0),
            reasons=reasons,
            default_config={},
        )


# ---------------------------------------------------------------------------
# Registry — all rules loaded by the analyzer
# ---------------------------------------------------------------------------

ALL_RULES: list[type[DetectionRule]] = [
    # Python
    DjangoRule,
    FlaskRule,
    FastAPIRule,
    # Node.js
    ExpressRule,
    NestJSRule,
    ReactRule,
    NextJSRule,
    VueRule,
    AngularRule,
    ViteRule,
    # PHP
    LaravelRule,
    # Java
    SpringBootRule,
    # Go
    GoRule,
    # Rust
    RustRule,
    # Ruby
    RubyRule,
    # .NET
    DotNetRule,
    # Infrastructure
    DockerRule,
    KubernetesRule,
]
