# US-003 WebSocket Server + Session Lifecycle

## Status

planned

## Lane

normal

## Product Contract

FastAPI WebSocket endpoint manages session lifecycle (connect → create session → process chunks → disconnect → cleanup). Each binary frame is processed through the interpret pipeline (US-001 + US-002) and responded to with a JSON result. Sessions are isolated by connection.

## Relevant Product Docs

- `docs/product/architecture.md`
- `docs/decisions/0008-chunk-overlap-strategy.md`

## Acceptance Criteria

- `WS /ws/interpret` accepts binary frames and returns JSON `{original, translated, language, latency_ms, entities}`.
- Each WebSocket connection gets its own `Session` with isolated `EntityMemory`.
- `Session` is cleaned up on disconnect — no memory leak.
- JSON config frame `{"action": "set_language", "direction": "en-vi"}` updates session language direction.
- Silent chunk result returned as `{original: "", translated: "", is_silent: true}` — no error.
- Latency measured from frame receipt to response send, included in every response.

## Design Notes

- Commands: `handle_audio_frame(session, bytes)`, `handle_config_frame(session, json)`
- Queries: none
- API: `WS /ws/interpret`
- Tables: none (in-memory session dict keyed by connection id)
- Domain rules: one session per WebSocket connection; session dict lives in app state
- UI surfaces: consumed by browser frontend (US-004)

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | `test_ws_handler.py`: mock interpret pipeline, assert response shape |
| Integration | `test_interpret_session.py`: inject mock Whisper + Claude clients, assert full pipeline result |
| E2E | Browser opens page, grants mic, speaks, sees translation within 3s |
| Platform | Manual demo |
| Release | Covered by `evaluate.py` latency metric |

## Harness Delta

None expected.

## Evidence

_Not yet implemented._
