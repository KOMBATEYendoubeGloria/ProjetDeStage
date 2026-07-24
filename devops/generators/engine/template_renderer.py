"""Template rendering layer using plain-string templates."""

from __future__ import annotations

from typing import Any, Mapping


class TemplateRenderer:
    """Minimal renderer that substitutes placeholders in templates."""

    def render(self, template: str, context: Mapping[str, Any]) -> str:
        rendered = template
        for key, value in context.items():
            placeholder = '{{' + key + '}}'
            rendered = rendered.replace(placeholder, str(value))
        return rendered
