# 0006 STT Provider — Whisper API vs Local

Date: 2026-05-26

## Status

Accepted

## Context

POC needs speech-to-text for EN and VI audio chunks (~2.5s each). Two viable options: OpenAI Whisper API (cloud) or whisper.cpp (local inference).

## Decision

Use OpenAI Whisper API (`whisper-1`).

## Alternatives Considered

1. **whisper.cpp local** — zero API cost, runs offline, but requires CUDA or Apple Silicon for <3s latency target. Windows CPU inference on 2.5s chunk: ~4-8s. Fails latency target.
2. **Google Speech-to-Text** — strong VI support but higher cost ($0.016/15s vs Whisper $0.006/min) and requires GCP setup.
3. **AssemblyAI** — good streaming support but no native VI model.

## Consequences

Positive:
- Zero local GPU required — runs on any machine
- Vietnamese support built-in (Whisper multilingual)
- ~500-800ms inference for 2.5s chunk → latency target met
- Simple REST API, minimal setup

Tradeoffs:
- API cost (mitigated: ~$0.72/2h session, far below $50 target)
- Requires internet connection
- Data sent to OpenAI (acceptable for internal meeting POC)

## Follow-Up

- If OnPoint requires on-premise: revisit whisper.cpp with GPU node
- Monitor `whisper-1` being superseded by newer model versions
