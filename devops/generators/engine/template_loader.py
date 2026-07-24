"""Template loading helpers for artifact generation."""

from __future__ import annotations

from pathlib import Path
from typing import Dict


class TemplateLoader:
    """Simple loader for plain-text templates stored in the project tree."""

    def __init__(self, templates_root: str | None = None) -> None:
        self.templates_root = Path(templates_root or Path(__file__).resolve().parents[1] / 'templates')

    def load(self, template_name: str) -> str:
        template_path = self.templates_root / template_name
        return template_path.read_text(encoding='utf-8')

    def available_templates(self) -> Dict[str, str]:
        return {path.name: str(path) for path in self.templates_root.rglob('*.j2') if path.is_file()}
