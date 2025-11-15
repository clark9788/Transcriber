"""Central configuration for the Medical Transcriber application."""

from __future__ import annotations

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
TRANSCRIPTIONS_DIR = BASE_DIR / "transcriptions"
RECORDINGS_DIR = BASE_DIR / "recordings"
AUDIT_LOG_DIR = BASE_DIR / "audit_logs"
TEMPLATES_DIR = BASE_DIR / "templates"

# Google Cloud
GCS_BUCKET = "transcribe_bucket9788"
LANGUAGE_CODE = "en-US"
GCS_MODEL = "medical_conversation"
POLL_INTERVAL_SEC = 5

# Audio recording defaults
SAMPLE_RATE = 16_000
CHANNELS = 1
AUDIO_SUBTYPE = "PCM_16"

# Security / deletion
SECURE_OVERWRITE_PASSES = 3

# Transcription cleaning - filler words to remove
FILLER_WORDS = [
    "um",
    "umm",
    "uh",
    "er",
    "ah",
    "eh",
    "a",  # Standalone "a" (will be handled carefully to avoid removing valid uses)
    "like",
    "you know",
    "well",
    "so",
    "actually",
    "basically",
]
