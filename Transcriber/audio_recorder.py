"""Audio recording utilities built on sounddevice + soundfile."""

from __future__ import annotations

import queue
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import sounddevice as sd
import soundfile as sf

from audit_logger import log
from config import AUDIO_SUBTYPE, CHANNELS, RECORDINGS_DIR, SAMPLE_RATE


class AudioRecorder:
    """Threaded WAV recorder that streams microphone audio to disk."""

    def __init__(self) -> None:
        self._queue: queue.Queue = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._recording = False
        self._current_file: Optional[Path] = None

    @property
    def current_file(self) -> Optional[Path]:
        return self._current_file

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _callback(self, indata, frames, time_info, status):  # pragma: no cover - sounddevice callback
        if status:
            print(status)
        self._queue.put(indata.copy())

    def start(self) -> Path:
        if self._recording:
            raise RuntimeError("Recording already in progress")
        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self._current_file = RECORDINGS_DIR / f"recording_{timestamp}.wav"
        self._recording = True
        self._thread = threading.Thread(target=self._record, daemon=True)
        self._thread.start()
        log("record_start", self._current_file, "", "Recording started")
        return self._current_file

    def _record(self) -> None:
        assert self._current_file is not None
        with sf.SoundFile(
            self._current_file,
            mode="w",
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            subtype=AUDIO_SUBTYPE,
        ) as destination:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                callback=self._callback,
            ):
                while self._recording:
                    try:
                        data = self._queue.get(timeout=0.1)
                        destination.write(data)
                    except queue.Empty:
                        continue

    def stop(self) -> Optional[Path]:
        if not self._recording:
            return self._current_file
        self._recording = False
        if self._thread:
            self._thread.join()
        log("record_stop", self._current_file or "", "", "Recording stopped")
        return self._current_file
