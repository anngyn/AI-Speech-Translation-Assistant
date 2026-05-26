# Product Overview — AI Interpreter

## Problem

OnPoint conducts large internal events (town halls, all-hands) in Vietnamese. Expat colleagues and the Thailand CREA team cannot follow. Professional cabin interpreter costs $1,000 per 2-hour session. Frequency is growing as the company scales regionally.

## Goal

Provide near-real-time EN↔VI interpretation via browser — no specialist hardware, no interpreter hire.

## Users

| User | Pain | Need |
| --- | --- | --- |
| Expat / Thai colleague | Cannot follow Vietnamese session | Read English translation in real-time |
| Vietnamese staff | Cannot follow expat speaker | Read Vietnamese translation in real-time |
| Meeting host | Interpreter cost, scheduling overhead | Self-serve tool, open in browser |

## Product Shape

Browser-based tool. User opens one URL, clicks Start, and sees a dual-panel view:
- Left panel: transcript in original language (as spoken)
- Right panel: translation in target language

Language direction is either auto-detected or manually set (EN→VI / VI→EN).

## Success Criteria

| Metric | Target |
| --- | --- |
| Transcription WER on meeting audio | < 10% |
| Key entity preservation (numbers, names, dates) | > 95% |
| Latency behind speaker | < 3 seconds |
| Cost per 2-hour session | < $50 (baseline: $1,000) |

## Constraints

- POC scope: single speaker at a time, one language per session direction
- No audio storage — chunks processed in memory, discarded after translation
- No auth required for POC
- Must run on localhost with a single `uvicorn main:app` command

## Out of Scope (POC)

- Simultaneous multi-speaker diarization
- Voice output (TTS)
- Mobile app
- Cloud deployment
- User accounts or session history persistence
