from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

from pydub import AudioSegment
from pydub import utils as pydub_utils

_WINGET_BIN = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links")
if os.path.isdir(_WINGET_BIN):
    os.environ.setdefault("PATH", "")
    if _WINGET_BIN not in os.environ["PATH"]:
        os.environ["PATH"] = _WINGET_BIN + os.pathsep + os.environ["PATH"]
    pydub_utils.get_prober_name()  # force re-detect after PATH update


TARGET_FRAME_RATE = 16_000
TARGET_CHANNELS = 1
TARGET_SAMPLE_WIDTH = 2
CHUNK_MS = 2_500


class PydubAudioConverter:
    def convert_to_wav(self, audio_bytes: bytes) -> bytes:
        return convert_to_wav(audio_bytes)


def convert_to_wav(audio_bytes: bytes, input_format: str | None = None) -> bytes:
    source = BytesIO(audio_bytes)
    if input_format is None:
        if audio_bytes[:4] == b"RIFF":
            input_format = "wav"
        elif audio_bytes[:4] == b"\x1a\x45\xdf\xa3":
            input_format = "webm"
        elif audio_bytes[:3] == b"OGG":
            input_format = "ogg"
    audio = AudioSegment.from_file(source, format=input_format)
    return segment_to_wav_bytes(audio)


def segment_to_wav_bytes(audio: AudioSegment) -> bytes:
    normalized = (
        audio.set_frame_rate(TARGET_FRAME_RATE)
        .set_channels(TARGET_CHANNELS)
        .set_sample_width(TARGET_SAMPLE_WIDTH)
    )
    out = BytesIO()
    normalized.export(out, format="wav")
    return out.getvalue()


def load_audio_file(path: str | Path) -> AudioSegment:
    return AudioSegment.from_file(path)


def slice_audio(audio: AudioSegment, chunk_ms: int = CHUNK_MS) -> list[bytes]:
    return [segment_to_wav_bytes(audio[start : start + chunk_ms]) for start in range(0, len(audio), chunk_ms)]
