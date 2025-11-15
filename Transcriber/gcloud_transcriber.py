"""Google Cloud Storage + Speech-to-Text integration."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Optional

from google.cloud import speech, storage
from google.cloud.speech_v1 import types

from audit_logger import log
from config import (
    GCS_BUCKET,
    GCS_MODEL,
    LANGUAGE_CODE,
    POLL_INTERVAL_SEC,
    SAMPLE_RATE,
)

SpeechStatusCallback = Optional[Callable[[str], None]]

speech_client = speech.SpeechClient()
storage_client = storage.Client()


def _set_status(callback: SpeechStatusCallback, message: str) -> None:
    if callback:
        callback(message)


def upload_and_transcribe(audio_path: Path, patient: str = "", status_cb: SpeechStatusCallback = None) -> str:
    """Upload an audio file, run transcription, return the transcript text."""
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(audio_path.name)

    _set_status(status_cb, "Uploading…")
    blob.upload_from_filename(str(audio_path))
    log("gcs_upload", audio_path, patient, "Uploaded to GCS")

    gcs_uri = f"gs://{GCS_BUCKET}/{audio_path.name}"
    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=types.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=LANGUAGE_CODE,
        model=GCS_MODEL,
        enable_automatic_punctuation=True,
    )

    _set_status(status_cb, "Transcribing…")
    operation = speech_client.long_running_recognize(config=config, audio=audio)

    while not operation.done():
        time.sleep(POLL_INTERVAL_SEC)
        _set_status(status_cb, "Transcribing…")

    _set_status(status_cb, "Processing result…")
    response = operation.result()

    transcript = "\n".join(
        alternative.transcript.strip()
        for result in response.results
        for alternative in result.alternatives[:1]
        if alternative.transcript.strip()
    )

    blob.delete()
    log("gcs_delete", audio_path.name, patient, "Deleted blob after transcription")
    _set_status(status_cb, "Completed")
    return transcript
