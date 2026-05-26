# US-001 Audio Ingest + STT Pipeline

## Status

planned

## Lane

normal

## Product Contract

Backend receives a WebM audio blob (~2.5s), converts to WAV (16kHz mono PCM), calls Whisper API with last-transcript context, and returns a structured transcript result. Silent/empty chunks are detected and skipped without calling Whisper.

## Relevant Product Docs

- `docs/product/overview.md`
- `docs/product/architecture.md`
- `docs/decisions/0006-stt-provider.md`
- `docs/decisions/0008-chunk-overlap-strategy.md`

## Acceptance Criteria

- Given a WebM audio blob, `audio_utils.convert_to_wav()` returns WAV bytes at 16kHz mono 16-bit PCM.
- Given WAV bytes with speech, `whisper_client.transcribe()` returns `ChunkResult` with non-empty `text` and detected `language`.
- Given WAV bytes with silence, `whisper_client.transcribe()` returns `ChunkResult` with empty `text` and `is_silent=True`.
- `prompt` field in Whisper call contains last transcript context when available.
- Whisper API errors are caught and returned as `ChunkResult(error=...)` — do not raise.

## Design Notes

- Commands: `transcribe(wav_bytes, last_transcript) → ChunkResult`
- Queries: none
- API: internal only (called by `interpret_session.py`)
- Tables: none
- Domain rules: silence = `text.strip() == ""` after Whisper response
- UI surfaces: none

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | `test_audio_utils.py`: WebM fixture → WAV format assertions (sample rate, channels, bit depth) |
| Integration | `test_whisper_client.py`: real Whisper API call with sample WAV, assert non-empty transcript |
| E2E | Covered by US-003 end-to-end flow |
| Platform | Manual mic test |
| Release | `evaluate.py` WER metric |

## Harness Delta

None expected.

## Evidence

_Not yet implemented._
