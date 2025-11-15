"""HIPAA-aligned audit logging utilities."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

from config import AUDIT_LOG_DIR

AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = AUDIT_LOG_DIR / "audit_log.csv"


def _ensure_header() -> None:
    if LOG_FILE.exists():
        return
    with LOG_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "action", "file", "patient", "details"])


def log(action: str, file_path: Union[str, Path], patient: str = "", details: str = "") -> None:
    """Append an audit row with UTC timestamp and metadata."""
    _ensure_header()
    timestamp = datetime.now(timezone.utc).isoformat()
    normalized = str(file_path)
    with LOG_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([timestamp, action, normalized, patient, details])
