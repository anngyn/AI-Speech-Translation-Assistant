# Test Matrix

## Status Values

| Status | Meaning |
| --- | --- |
| planned | Accepted as intended behavior, not implemented |
| in_progress | Actively being built |
| implemented | Implemented and proof exists |
| changed | Contract changed after earlier implementation |
| retired | No longer part of the product contract |

## Matrix

| Story | Contract | Unit | Integration | E2E | Platform | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US-001 | WebM → WAV → Whisper → ChunkResult | yes | yes | via US-003 | manual mic | implemented | Browser now sends PCM WAV 16kHz via Web Audio API; `no_speech_prob` hallucination filter applied; `TranscriptionSegment` getattr fix |
| US-002 | Transcript → EntityMemory → Bedrock Claude → TranslationResult | yes | yes | via US-003 | manual speak | in_progress | Bedrock boundary test added; live AWS proof pending |
| US-003 | WS binary frame → JSON response, session isolation | yes | yes | manual browser | manual | implemented | WebSocket connect confirmed; WebM header prepend removed (client sends WAV directly) |
| US-004 | Browser mic → dual-panel display < 3s | n/a | n/a | manual | Chrome/Edge | implemented | wsUrl() uses location.host (no hardcoded port); fetch URL same fix |
| US-005 | File upload → SSE stream chunks | yes | yes | manual upload | manual | planned | none |
| US-006 | evaluate.py → WER/latency/cost report | n/a | n/a | run script | manual | planned | none |

## Evidence Rules

- Unit proof: pure domain and application logic
- Integration proof: real API calls (Whisper, Claude) with sample data
- E2E proof: browser open → speech → translation displayed
- Platform proof: manual demo only for POC scope
- Release: `evaluate.py` report output
