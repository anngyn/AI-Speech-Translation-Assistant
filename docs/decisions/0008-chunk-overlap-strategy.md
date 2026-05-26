# 0008 Audio Chunk Size and Overlap Strategy

Date: 2026-05-26

## Status

Accepted

## Context

Real-time STT requires splitting continuous audio into discrete chunks. Chunk size directly controls latency vs accuracy tradeoff. Chunk boundary cuts words mid-sentence, hurting WER and entity preservation.

## Decision

- Chunk size: **2500ms**
- Overlap: **500ms** (last 500ms of chunk N prepended to chunk N+1)
- Whisper `prompt` field: last 1-2 sentences of previous transcript injected

## Alternatives Considered

1. **1000ms chunks** — lower latency (~1.5s total) but Whisper accuracy degrades badly on short fragments; word boundary problem severe; cost doubles.
2. **5000ms chunks** — better accuracy but total latency (chunk wait + STT + translate) exceeds 3s target.
3. **VAD (Voice Activity Detection) based chunking** — most accurate, splits on silence. Adds complexity, requires `webrtcvad` or `silero-vad`. Out of scope for POC.
4. **No overlap** — simpler but entity names split across boundaries fail preservation target.

## Consequences

Positive:
- 2500ms + 500-800ms STT + 300-500ms translation = ~1.5-1.8s total latency. Well within 3s.
- Overlap + Whisper prompt = entity boundary preservation significantly improved
- 2500ms chunks = 48 Whisper calls/2h session direction — negligible cost

Tradeoffs:
- Overlap means ~17% of audio is processed twice (accepted)
- Backend must dedup stitched transcript to remove overlap repetition

## Follow-Up

- If VAD is added later, remove overlap logic — VAD boundary is more accurate
- Consider increasing to 3000ms if WER target is not met in evaluation
