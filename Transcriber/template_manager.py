"""Utilities for loading and applying transcription templates."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Mapping

from config import TEMPLATES_DIR

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")


def load_templates() -> Dict[str, Path]:
    """Return a mapping of template name to file path."""
    if not TEMPLATES_DIR.exists():
        return {}
    return {path.stem: path for path in TEMPLATES_DIR.glob("*.txt")}


def apply_template(template_path: Path, transcript: str, context: Mapping[str, str] | None = None) -> str:
    """Merge transcript + optional context into the chosen template."""
    raw = template_path.read_text(encoding="utf-8")
    replacements = dict(context or {})
    replacements.setdefault("TRANSCRIPT", transcript)

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return replacements.get(key, "")

    return PLACEHOLDER_PATTERN.sub(_replace, raw)
