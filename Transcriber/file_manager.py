"""Transcription file management and secure deletion helpers."""

from __future__ import annotations

import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from audit_logger import log
from config import (
    RECORDINGS_DIR,
    SECURE_OVERWRITE_PASSES,
    TRANSCRIPTIONS_DIR,
)

for directory in (TRANSCRIPTIONS_DIR, RECORDINGS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

SANITIZE_PATTERN = re.compile(r"[^A-Za-z0-9_-]+")


def sanitize_component(value: str) -> str:
    cleaned = SANITIZE_PATTERN.sub("_", value.strip())
    return cleaned or "unknown"


def generate_filename(patient: str, dob: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_patient = sanitize_component(patient)
    safe_dob = sanitize_component(dob)
    return TRANSCRIPTIONS_DIR / f"{safe_patient}_{safe_dob}_{timestamp}.txt"


def list_transcriptions() -> List[Path]:
    files = list(TRANSCRIPTIONS_DIR.glob("*.txt"))
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return files


def save_transcription(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    log("save_transcription", path, "", "Saved transcription")


def load_transcription(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def secure_delete(file_path: Path, patient: str = "") -> None:
    if not file_path.exists():
        return
    size = file_path.stat().st_size
    if size > 0:
        with file_path.open("r+b") as handle:
            for _ in range(SECURE_OVERWRITE_PASSES):
                handle.seek(0)
                handle.write(secrets.token_bytes(size))
                handle.flush()
                os.fsync(handle.fileno())
    try:
        file_path.unlink()
    except FileNotFoundError:
        return
    log(
        "secure_delete",
        file_path,
        patient,
        f"Overwritten {SECURE_OVERWRITE_PASSES} passes and deleted",
    )
