"""Comprehensive tests for the Technology Detection Engine (Phase S1.1)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase, TestCase

from devops.generators.analyzer.project_analyzer import ProjectAnalyzer
from devops.generators.analyzer.rules import (
    ALL_RULES,
    DetectionResult,
    DetectionRule,
    DjangoRule,
    FlaskRule,
    FastAPIRule,
    ExpressRule,
    NestJSRule,
    ReactRule,
    NextJSRule,
    VueRule,
    AngularRule,
    ViteRule,
    LaravelRule,
    SpringBootRule,
    GoRule,
    RustRule,
    RubyRule,
    DotNetRule,
    DockerRule,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(root: Path, files: dict[str, str]) -> None:
    """Write *files* (relative_path → content) into *root*."""
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')


# ===========================================================================
# Individual rule tests
# ===========================================================================

class DjangoRuleTests(SimpleTestCase):
    def setUp(self):
        self.rule = DjangoRule()

    def test_detect_django_manage_py(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'manage.py': '#!/usr/bin/env python\nimport django\nfrom django.core.management import execute_from_command_line',
                'requirements.txt': 'django==4.2\npsycopg2',
            })
            filenames = {'manage.py', 'requirements.txt'}
            contents = {
                'manage.py': (root / 'manage.py').read_text(),
                'requirements.txt': (root / 'requirements.txt').read_text(),
            }
            result = self.rule.detect(root, filenames, contents)
            self.assertIsNotNone(result)
            self.assertEqual(result.name, 'django')
            self.assertGreater(result.confidence, 0.4)

    def test_no_django_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {'readme.md': 'hello'})
            result = self.rule.detect(root, {'readme.md'}, {'readme.md': 'hello'})
            self.assertIsNone(result)


class FlaskRuleTests(SimpleTestCase):
    def setUp(self):
        self.rule = FlaskRule()

    def test_detect_flask_from_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'requirements.txt': 'flask==3.0\nwerkzeug',
                'app.py': 'from flask import Flask\napp = Flask(__name__)',
            })
            filenames = {'requirements.txt', 'app.py'}
            contents = {f: (root / f).read_text() for f in filenames}
            result = self.rule.detect(root, filenames, contents)
            self.assertIsNotNone(result)
            self.assertEqual(result.name, 'flask')
            self.assertGreater(result.confidence, 0.4)

    def test_no_flask_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = self.rule.detect(root, set(), {})
            self.assertIsNone(result)


class FastAPIRuleTests(SimpleTestCase):
    def setUp(self):
        self.rule = FastAPIRule()

    def test_detect_fastapi(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'requirements.txt': 'fastapi==0.108\nuvicorn',
                'main.py': 'from fastapi import FastAPI\napp = FastAPI()',
            })
            filenames = {'requirements.txt', 'main.py'}
            contents = {f: (root / f).read_text() for f in filenames}
            result = self.rule.detect(root, filenames, contents)
            self.assertIsNotNone(result)
            self.assertEqual(result.name, 'fastapi')

    def test_no_fastapi_returns_none(self):
        result = self.rule.detect(Path('.'), set(), {})
        self.assertIsNone(result)


class ExpressRuleTests(SimpleTestCase):
    def setUp(self):
        self.rule = ExpressRule()

    def test_detect_express(self):
        pkg = json.dumps({
            'name': 'my-app',
            'dependencies': {'express': '^4.18.0', 'body-parser': '^1.20.0'},
            'scripts': {'start': 'node server.js'},
        })
        result = self.rule.detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'express')
        self.assertGreater(result.confidence, 0.5)

    def test_no_package_json_returns_none(self):
        result = self.rule.detect(Path('.'), set(), {})
        self.assertIsNone(result)

    def test_package_without_express_returns_none(self):
        pkg = json.dumps({'dependencies': {'lodash': '^4.17.0'}})
        result = self.rule.detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNone(result)


class NestJSRuleTests(SimpleTestCase):
    def test_detect_nestjs(self):
        pkg = json.dumps({'dependencies': {'@nestjs/core': '^10.0.0', '@nestjs/common': '^10.0.0'}})
        result = NestJSRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'nestjs')

    def test_no_nestjs_returns_none(self):
        pkg = json.dumps({'dependencies': {'express': '^4.0.0'}})
        result = NestJSRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNone(result)


class ReactRuleTests(SimpleTestCase):
    def test_detect_react(self):
        pkg = json.dumps({
            'dependencies': {'react': '^18.2.0', 'react-dom': '^18.2.0', 'react-scripts': '5.0.1'},
        })
        result = ReactRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'react')

    def test_react_without_react_dom_not_detected(self):
        pkg = json.dumps({'dependencies': {'react': '^18.2.0'}})
        result = ReactRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNone(result)

    def test_not_react_project(self):
        pkg = json.dumps({'dependencies': {'express': '^4.0.0'}})
        result = ReactRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNone(result)


class NextJSRuleTests(SimpleTestCase):
    def test_detect_nextjs(self):
        pkg = json.dumps({'dependencies': {'next': '14.0.0', 'react': '^18.2.0'}})
        result = NextJSRule().detect(
            Path('.'), {'package.json', 'next.config.js'}, {'package.json': pkg}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'nextjs')
        self.assertGreater(result.confidence, 0.8)

    def test_no_next_returns_none(self):
        pkg = json.dumps({'dependencies': {'react': '^18.0.0'}})
        result = NextJSRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNone(result)


class VueRuleTests(SimpleTestCase):
    def test_detect_vue(self):
        pkg = json.dumps({'dependencies': {'vue': '^3.3.0'}})
        result = VueRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'vue')

    def test_no_vue_returns_none(self):
        pkg = json.dumps({'dependencies': {'react': '^18.0.0'}})
        result = VueRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNone(result)


class AngularRuleTests(SimpleTestCase):
    def test_detect_angular(self):
        pkg = json.dumps({'dependencies': {'@angular/core': '^17.0.0'}})
        result = AngularRule().detect(
            Path('.'), {'package.json', 'angular.json'}, {'package.json': pkg}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'angular')
        self.assertGreater(result.confidence, 0.8)

    def test_no_angular_returns_none(self):
        pkg = json.dumps({'dependencies': {'react': '^18.0.0'}})
        result = AngularRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNone(result)


class ViteRuleTests(SimpleTestCase):
    def test_detect_vite(self):
        pkg = json.dumps({'devDependencies': {'vite': '^5.0.0'}})
        result = ViteRule().detect(
            Path('.'), {'package.json', 'vite.config.ts'}, {'package.json': pkg}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'vite')

    def test_no_vite_returns_none(self):
        pkg = json.dumps({'dependencies': {'react': '^18.0.0'}})
        result = ViteRule().detect(Path('.'), {'package.json'}, {'package.json': pkg})
        self.assertIsNone(result)


class LaravelRuleTests(SimpleTestCase):
    def test_detect_laravel(self):
        composer = json.dumps({'require': {'laravel/framework': '^10.0'}})
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {'artisan': '#!/usr/bin/env php'})
            filenames = {'artisan', 'composer.json'}
            contents = {'composer.json': composer, 'artisan': (root / 'artisan').read_text()}
            result = LaravelRule().detect(root, filenames, contents)
            self.assertIsNotNone(result)
            self.assertEqual(result.name, 'laravel')
            self.assertGreater(result.confidence, 0.5)

    def test_no_laravel_returns_none(self):
        result = LaravelRule().detect(Path('.'), set(), {})
        self.assertIsNone(result)


class SpringBootRuleTests(SimpleTestCase):
    def test_detect_spring_boot_from_pom(self):
        pom = '<project><dependencies><dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency></dependencies></project>'
        result = SpringBootRule().detect(Path('.'), {'pom.xml'}, {'pom.xml': pom})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'springboot')

    def test_detect_spring_boot_from_gradle(self):
        gradle = "plugins { id 'org.springframework.boot' version '3.2.0' }"
        result = SpringBootRule().detect(Path('.'), {'build.gradle'}, {'build.gradle': gradle})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'springboot')

    def test_no_spring_returns_none(self):
        result = SpringBootRule().detect(Path('.'), set(), {})
        self.assertIsNone(result)


class GoRuleTests(SimpleTestCase):
    def test_detect_go(self):
        gomod = 'module example.com/myapp\n\ngo 1.21'
        result = GoRule().detect(Path('.'), {'go.mod'}, {'go.mod': gomod})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'go')

    def test_no_go_returns_none(self):
        result = GoRule().detect(Path('.'), set(), {})
        self.assertIsNone(result)


class RustRuleTests(SimpleTestCase):
    def test_detect_rust(self):
        cargo = '[package]\nname = "myapp"\nversion = "0.1.0"'
        result = RustRule().detect(Path('.'), {'Cargo.toml'}, {'Cargo.toml': cargo})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'rust')

    def test_no_rust_returns_none(self):
        result = RustRule().detect(Path('.'), set(), {})
        self.assertIsNone(result)


class RubyRuleTests(SimpleTestCase):
    def test_detect_ruby(self):
        gemfile = "source 'https://rubygems.org'\ngem 'rails', '~> 7.0'"
        result = RubyRule().detect(Path('.'), {'Gemfile'}, {'Gemfile': gemfile})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'ruby')

    def test_no_ruby_returns_none(self):
        result = RubyRule().detect(Path('.'), set(), {})
        self.assertIsNone(result)


class DotNetRuleTests(SimpleTestCase):
    def test_detect_dotnet(self):
        csproj = '<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>'
        result = DotNetRule().detect(
            Path('.'), {'MyApp.csproj', 'Program.cs'}, {'MyApp.csproj': csproj}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'dotnet')

    def test_no_dotnet_returns_none(self):
        result = DotNetRule().detect(Path('.'), set(), {})
        self.assertIsNone(result)


class DockerRuleTests(SimpleTestCase):
    def test_detect_dockerfile(self):
        result = DockerRule().detect(Path('.'), {'Dockerfile'}, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'docker')

    def test_detect_compose(self):
        result = DockerRule().detect(Path('.'), {'docker-compose.yml'}, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'docker')

    def test_no_docker_returns_none(self):
        result = DockerRule().detect(Path('.'), set(), {})
        self.assertIsNone(result)


# ===========================================================================
# Full ProjectAnalyzer tests
# ===========================================================================

class ProjectAnalyzerEmptyProjectTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_empty_directory_returns_generic(self):
        with tempfile.TemporaryDirectory() as td:
            result = self.analyzer.analyze_directory(Path(td))
            self.assertEqual(result['framework'], 'generic')
            self.assertEqual(result['confidence'], 0.0)
            self.assertEqual(result['type'], 'generic')

    def test_only_readme_returns_generic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {'README.md': '# My Project'})
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'generic')


class ProjectAnalyzerDjangoTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_django_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'manage.py': 'import django\nfrom django.core.management import execute_from_command_line',
                'requirements.txt': 'django==4.2\npsycopg2-binary\nrest-framework',
                'settings.py': 'INSTALLED_APPS = ["django.contrib.admin"]\nMIDDLEWARE = []',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'django')
            self.assertEqual(result['language'], 'python')
            self.assertEqual(result['ports'], [8000])
            self.assertGreater(result['confidence'], 0.3)
            self.assertTrue(len(result['detection_reasons']) > 0)

    def test_django_with_pyproject_toml(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'pyproject.toml': '[project]\nname = "myapp"\ndependencies = ["django>=4.2"]',
                'manage.py': 'from django.core.management import execute_from_command_line',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'django')


class ProjectAnalyzerFlaskTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_flask_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'requirements.txt': 'flask==3.0.0\njinja2',
                'app.py': 'from flask import Flask\napp = Flask(__name__)\n@app.route("/")\ndef hello(): return "hi"',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'flask')
            self.assertEqual(result['language'], 'python')
            self.assertIn('flask', result['stack'])


class ProjectAnalyzerFastAPITests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_fastapi_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'requirements.txt': 'fastapi==0.108\nuvicorn',
                'main.py': 'from fastapi import FastAPI\napp = FastAPI()\n@app.get("/")\ndef root(): return {"hello": "world"}',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'fastapi')
            self.assertEqual(result['language'], 'python')
            self.assertIn('fastapi', result['stack'])


class ProjectAnalyzerExpressTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_express_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'name': 'my-api',
                'dependencies': {'express': '^4.18.0', 'cors': '^2.8.5'},
                'scripts': {'start': 'node server.js'},
            })
            _make_project(root, {'package.json': pkg})
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'express')
            self.assertEqual(result['language'], 'javascript')
            self.assertEqual(result['ports'], [3000])

    def test_detect_nestjs_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'dependencies': {'@nestjs/core': '^10.0.0', '@nestjs/common': '^10.0.0'},
            })
            _make_project(root, {
                'package.json': pkg,
                'nest-cli.json': '{"collection": "@nestjs/schematics"}',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'nestjs')
            self.assertEqual(result['language'], 'typescript')


class ProjectAnalyzerReactTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_react_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'name': 'react-app',
                'dependencies': {'react': '^18.2.0', 'react-dom': '^18.2.0', 'react-scripts': '5.0.1'},
                'scripts': {'start': 'react-scripts start', 'build': 'react-scripts build'},
            })
            _make_project(root, {'package.json': pkg})
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'react')
            self.assertIn('react', result['stack'])


class ProjectAnalyzerNextJSTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_nextjs_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'dependencies': {'next': '14.0.0', 'react': '^18.2.0', 'react-dom': '^18.2.0'},
            })
            _make_project(root, {
                'package.json': pkg,
                'next.config.js': 'module.exports = { reactStrictMode: true }',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'nextjs')
            self.assertIn('nextjs', result['stack'])


class ProjectAnalyzerVueTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_vue_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'dependencies': {'vue': '^3.3.0', 'vue-router': '^4.2.0'},
            })
            _make_project(root, {
                'package.json': pkg,
                'vue.config.js': 'module.exports = {}',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'vue')
            self.assertIn('vue', result['stack'])


class ProjectAnalyzerAngularTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_angular_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'dependencies': {'@angular/core': '^17.0.0', '@angular/common': '^17.0.0'},
            })
            _make_project(root, {
                'package.json': pkg,
                'angular.json': '{"projects": {}}',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'angular')
            self.assertEqual(result['ports'], [4200])


class ProjectAnalyzerLaravelTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_laravel_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            composer = json.dumps({'require': {'laravel/framework': '^10.0'}})
            _make_project(root, {
                'composer.json': composer,
                'artisan': '#!/usr/bin/env php',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'laravel')
            self.assertEqual(result['language'], 'php')
            self.assertEqual(result['database'], 'mysql')


class ProjectAnalyzerSpringBootTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_springboot_from_pom(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pom = '<project><dependencies><dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency></dependencies></project>'
            _make_project(root, {'pom.xml': pom})
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'springboot')
            self.assertEqual(result['language'], 'java')
            self.assertEqual(result['ports'], [8080])

    def test_detect_springboot_from_gradle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gradle = "plugins { id 'org.springframework.boot' version '3.2.0' }\ndependencies { implementation 'org.springframework.boot:spring-boot-starter-web' }"
            _make_project(root, {'build.gradle': gradle})
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['framework'], 'springboot')


class ProjectAnalyzerGoTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_go_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'go.mod': 'module example.com/myapp\n\ngo 1.21',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['language'], 'go')
            self.assertIn('go', result['stack'])


class ProjectAnalyzerRustTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_rust_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'Cargo.toml': '[package]\nname = "myapp"\nversion = "0.1.0"',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['language'], 'rust')
            self.assertIn('rust', result['stack'])


class ProjectAnalyzerRubyTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_ruby_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'Gemfile': "source 'https://rubygems.org'\ngem 'rails', '~> 7.0'",
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['language'], 'ruby')
            self.assertIn('ruby', result['stack'])


class ProjectAnalyzerDotNetTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_dotnet_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'MyApp.csproj': '<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>',
                'Program.cs': 'var builder = WebApplication.CreateBuilder(args);',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['language'], 'csharp')
            self.assertIn('dotnet', result['stack'])


# ===========================================================================
# Fullstack detection tests
# ===========================================================================

class FullstackDjangoReactTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_detect_django_react_stack(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'dependencies': {'react': '^18.2.0', 'react-dom': '^18.2.0'},
            })
            _make_project(root, {
                'manage.py': 'from django.core.management import execute_from_command_line',
                'requirements.txt': 'django==4.2',
                'package.json': pkg,
            })
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result['primary_framework'], 'django')
            self.assertIn('react', result['stack'])
            self.assertIn('react', result.get('secondary_frameworks', []))

    def test_detect_fastapi_vue_stack(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'dependencies': {'vue': '^3.3.0', 'vue-router': '^4.2.0'},
            })
            _make_project(root, {
                'requirements.txt': 'fastapi==0.108\nuvicorn',
                'main.py': 'from fastapi import FastAPI\napp = FastAPI()',
                'package.json': pkg,
            })
            result = self.analyzer.analyze_directory(root)
            self.assertIn('fastapi', result['stack'])
            self.assertIn('vue', result['stack'])


# ===========================================================================
# False positive tests
# ===========================================================================

class FalsePositiveTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_react_project_not_detected_as_django(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({
                'name': 'my-react-app',
                'dependencies': {'react': '^18.2.0', 'react-dom': '^18.2.0'},
            })
            _make_project(root, {'package.json': pkg})
            result = self.analyzer.analyze_directory(root)
            self.assertNotEqual(result['framework'], 'django')
            self.assertNotEqual(result['language'], 'python')

    def test_express_project_not_detected_as_django(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = json.dumps({'dependencies': {'express': '^4.18.0'}})
            _make_project(root, {'package.json': pkg})
            result = self.analyzer.analyze_directory(root)
            self.assertNotEqual(result['framework'], 'django')
            self.assertNotEqual(result['language'], 'python')

    def test_laravel_project_not_detected_as_django(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            composer = json.dumps({'require': {'laravel/framework': '^10.0'}})
            _make_project(root, {'composer.json': composer, 'artisan': '#!/usr/bin/env php'})
            result = self.analyzer.analyze_directory(root)
            self.assertNotEqual(result['framework'], 'django')

    def test_springboot_not_detected_as_django(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pom = '<project><dependency><groupId>org.springframework.boot</groupId></dependency></project>'
            _make_project(root, {'pom.xml': pom})
            result = self.analyzer.analyze_directory(root)
            self.assertNotEqual(result['framework'], 'django')

    def test_go_project_not_detected_as_python(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {'go.mod': 'module example.com/app\n\ngo 1.21'})
            result = self.analyzer.analyze_directory(root)
            self.assertNotEqual(result['language'], 'python')

    def test_rust_project_not_detected_as_python(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {'Cargo.toml': '[package]\nname = "app"'})
            result = self.analyzer.analyze_directory(root)
            self.assertNotEqual(result['language'], 'python')


# ===========================================================================
# enrich_project_metadata tests
# ===========================================================================

class EnrichProjectMetadataTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_enrich_django_dict(self):
        project = {'name': 'myapp', 'framework': 'django'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'python')
        self.assertEqual(result['ports'], [8000])
        self.assertEqual(result['database'], 'postgres')

    def test_enrich_flask_dict(self):
        project = {'name': 'myapp', 'framework': 'flask'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'python')
        self.assertEqual(result['ports'], [5000])

    def test_enrich_fastapi_dict(self):
        project = {'name': 'myapp', 'framework': 'fastapi'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'python')
        self.assertEqual(result['ports'], [8000])

    def test_enrich_express_dict(self):
        project = {'name': 'myapp', 'framework': 'express'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'javascript')
        self.assertEqual(result['ports'], [3000])

    def test_enrich_nestjs_dict(self):
        project = {'name': 'myapp', 'framework': 'nestjs'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'typescript')
        self.assertEqual(result['ports'], [3000])

    def test_enrich_react_dict(self):
        project = {'name': 'frontend', 'framework': 'react'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['ports'], [80])

    def test_enrich_nextjs_dict(self):
        project = {'name': 'myapp', 'framework': 'nextjs'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'typescript')
        self.assertEqual(result['ports'], [3000])

    def test_enrich_vue_dict(self):
        project = {'name': 'myapp', 'framework': 'vue'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'javascript')
        self.assertEqual(result['ports'], [3000])

    def test_enrich_angular_dict(self):
        project = {'name': 'myapp', 'framework': 'angular'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'typescript')
        self.assertEqual(result['ports'], [4200])

    def test_enrich_laravel_dict(self):
        project = {'name': 'api', 'framework': 'laravel'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'php')
        self.assertEqual(result['database'], 'mysql')

    def test_enrich_springboot_dict(self):
        project = {'name': 'svc', 'framework': 'springboot'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['ports'], [8080])

    def test_enrich_go_dict(self):
        project = {'name': 'goservice', 'framework': 'go'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'go')
        self.assertEqual(result['ports'], [8080])

    def test_enrich_rust_dict(self):
        project = {'name': 'rustsvc', 'framework': 'rust'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'rust')

    def test_enrich_ruby_dict(self):
        project = {'name': 'rubyapp', 'framework': 'ruby'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'ruby')

    def test_enrich_dotnet_dict(self):
        project = {'name': 'dotnetapp', 'framework': 'dotnet'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'csharp')
        self.assertEqual(result['ports'], [5000])

    def test_fills_missing_provider_and_ci(self):
        project = {'name': 'app', 'framework': 'django'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['provider'], 'docker')
        self.assertEqual(result['ci_platform'], 'github-actions')

    def test_enrich_defaults_to_generic_when_no_framework(self):
        project = {'name': 'mystery'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['framework'], 'generic')
        self.assertEqual(result['language'], 'python')


# ===========================================================================
# analyze() method with dict input
# ===========================================================================

class AnalyzeMethodTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_analyze_with_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'manage.py': 'from django.core.management import execute_from_command_line',
                'requirements.txt': 'django==4.2',
            })
            result = self.analyzer.analyze(str(root))
            self.assertEqual(result['framework'], 'django')

    def test_analyze_with_dict(self):
        project = {'name': 'myapp', 'framework': 'fastapi'}
        result = self.analyzer.analyze(project)
        self.assertEqual(result['framework'], 'fastapi')
        self.assertEqual(result['language'], 'python')


# ===========================================================================
# Rule registry tests
# ===========================================================================

class RuleRegistryTests(SimpleTestCase):
    def test_all_rules_is_non_empty(self):
        self.assertGreater(len(ALL_RULES), 0)

    def test_all_rules_are_subclasses_of_detection_rule(self):
        for rule_cls in ALL_RULES:
            self.assertTrue(
                issubclass(rule_cls, DetectionRule),
                f'{rule_cls} is not a DetectionRule subclass',
            )

    def test_analyzer_uses_all_rules_by_default(self):
        analyzer = ProjectAnalyzer()
        self.assertEqual(len(analyzer._rules), len(ALL_RULES))

    def test_custom_rules_injection(self):
        class FakeRule(DetectionRule):
            name = 'fake'
            category = 'framework'
            def detect(self, root, filenames, contents):
                return DetectionResult(name='fake', confidence=0.99, reasons=['test'], default_config={})

        analyzer = ProjectAnalyzer(rules=[FakeRule()])
        with tempfile.TemporaryDirectory() as td:
            result = analyzer.analyze_directory(Path(td))
            self.assertEqual(result['framework'], 'fake')
            self.assertIn('fake', result['stack'])


# ===========================================================================
# Detection result dataclass tests
# ===========================================================================

class DetectionResultTests(SimpleTestCase):
    def test_detection_result_creation(self):
        dr = DetectionResult(
            name='django',
            confidence=0.95,
            reasons=['manage.py found'],
            default_config={'language': 'python', 'ports': [8000]},
        )
        self.assertEqual(dr.name, 'django')
        self.assertEqual(dr.confidence, 0.95)
        self.assertEqual(dr.reasons, ['manage.py found'])
        self.assertEqual(dr.default_config['language'], 'python')

    def test_detection_result_default_config_is_empty_dict(self):
        dr = DetectionResult(name='test', confidence=0.5, reasons=[])
        self.assertEqual(dr.default_config, {})


# ===========================================================================
# Backward-compatibility: existing tests patterns must still work
# ===========================================================================

class BackwardCompatibilityTests(SimpleTestCase):
    """Ensure the existing test patterns from test_generator_engine.py still pass."""

    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_enrich_django_dict(self):
        project = {'name': 'myapp', 'framework': 'django'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'python')
        self.assertEqual(result['ports'], [8000])
        self.assertEqual(result['database'], 'postgres')

    def test_enrich_nodejs_dict(self):
        project = {'name': 'myapp', 'framework': 'nodejs'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'javascript')
        self.assertEqual(result['ports'], [3000])

    def test_enrich_react_dict(self):
        project = {'name': 'frontend', 'framework': 'react'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['ports'], [80])

    def test_enrich_laravel_dict(self):
        project = {'name': 'api', 'framework': 'laravel'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'php')
        self.assertEqual(result['database'], 'mysql')

    def test_enrich_springboot_dict(self):
        project = {'name': 'svc', 'framework': 'springboot'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['language'], 'java')
        self.assertEqual(result['ports'], [8080])

    def test_fills_missing_provider_and_ci(self):
        project = {'name': 'app', 'framework': 'django'}
        result = self.analyzer.enrich_project_metadata(project)
        self.assertEqual(result['provider'], 'docker')
        self.assertEqual(result['ci_platform'], 'github-actions')


# ===========================================================================
# Infrastructure detection
# ===========================================================================

class InfrastructureDetectionTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = ProjectAnalyzer()

    def test_docker_infrastructure_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {
                'Dockerfile': 'FROM python:3.11\nWORKDIR /app',
                'docker-compose.yml': 'version: "3.9"\nservices:\n  app:\n    build: .',
            })
            result = self.analyzer.analyze_directory(root)
            self.assertIn('docker', result.get('infra', []))

    def test_no_infrastructure_when_absent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_project(root, {'readme.md': 'hello'})
            result = self.analyzer.analyze_directory(root)
            self.assertEqual(result.get('infra', []), [])
