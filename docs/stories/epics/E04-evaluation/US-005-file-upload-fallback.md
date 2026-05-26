# US-005 File Upload Fallback

## Status

planned

## Lane

normal

## Product Contract

REST endpoint accepts an audio file upload (MP3, WAV, MP4). Backend slices it into 2500ms chunks and streams results via Server-Sent Events (SSE). Frontend shows same dual-panel display as live mic mode. Enables demo without microphone and evaluation against known audio.

## Relevant Product Docs

- `docs/product/architecture.md`

## Acceptance Criteria

- `POST /interpret/file` accepts multipart form with audio file.
- File is sliced into 2500ms WAV chunks via `audio_utils`.
- Each chunk processed through same interpret pipeline as WebSocket path.
- Results streamed as SSE `data:` events in same JSON shape as WebSocket.
- Frontend file upload mode activated by drag-drop or file picker — switches from mic mode.

## Design Notes

- API: `POST /interpret/file` → SSE stream
- Reuses `interpret_session.py` — no duplicate pipeline logic
- `audio_router.py` handles multipart, slicing, and SSE response

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | `test_audio_utils.py`: slice 10s WAV → 4 chunks of 2500ms each |
| Integration | Upload sample MP3 → assert SSE stream contains N events |
| E2E | Manual: upload `sample_meeting.mp3`, observe streaming translation |
| Platform | Manual |
| Release | Used by `evaluate.py` as input mechanism |

## Harness Delta

None expected.

## Evidence

_Not yet implemented._
