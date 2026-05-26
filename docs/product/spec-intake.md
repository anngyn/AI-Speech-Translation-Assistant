# Spec Intake — AI Interpreter

Date: 2026-05-26

## Source

- Attached file: `AI Engineer Fresher & Intern - Assignment - Fall 2026.pdf`
- Problem selected: Problem 1 — The AI Interpreter

## Project Summary

Build a near-real-time EN↔VI interpretation tool for OnPoint internal events. OnPoint acquired CREA (Thailand) — expat and Thai colleagues cannot follow Vietnamese-only town halls. Professional interpreter costs $1,000/2h. This tool targets <$50/session via Whisper STT + Claude Haiku on Amazon Bedrock with session-scoped entity memory.

## Candidate Product Docs

| File | Purpose | Source sections |
| --- | --- | --- |
| `docs/product/overview.md` | Goals, users, constraints, success criteria | Assignment spec + evaluation criteria |
| `docs/product/architecture.md` | Stack, data flow, component boundaries | Architecture decisions |
| `docs/product/evaluation.md` | WER, latency, cost, entity preservation targets | Assignment evaluation table |

## Candidate Epics

| Epic | Description | Status |
| --- | --- | --- |
| E01 | Audio capture + chunked STT pipeline | unsliced |
| E02 | Context agent + EN↔VI translation with entity memory | unsliced |
| E03 | WebSocket server + browser frontend | unsliced |
| E04 | File upload fallback + evaluation script | unsliced |

## Architecture Questions

- Runtime stack: Python 3.11 + FastAPI backend, vanilla HTML/JS frontend
- Product surfaces: Browser (WebSocket client)
- Storage: In-memory session dict only — no persistence needed for POC
- External providers: OpenAI Whisper API (STT), Amazon Bedrock Runtime hosting Anthropic Claude Haiku 4.5 (translation)
- Deployment target: localhost for POC
- Security model: OpenAI key plus AWS credential chain for Bedrock; no end-user auth for POC scope

## Validation Shape

| Layer | Expected proof |
| --- | --- |
| Unit | EntityMemory accumulation, audio_utils WebM→WAV conversion |
| Integration | Whisper API call returns transcript, Claude API returns translation |
| E2E | Mic audio → dual-panel display in browser within 3s |
| Platform | Manual demo: mic or sample audio file |
| Release | `evaluate.py` report: WER, entity preservation %, avg latency, cost estimate |

## Open Decisions

- D-0006: STT provider choice (Whisper API vs local whisper.cpp)
- D-0007: Translation model choice (Claude Haiku vs GPT-4o-mini)
- D-0008: Audio chunk size and overlap strategy
- D-0009: Frontend framework (vanilla HTML vs React)
- D-0010: Claude Haiku access path (Amazon Bedrock Runtime vs direct Anthropic API)

## First Story Candidates

- US-001: Audio ingest + STT (backend core)
- US-002: Entity memory + context-aware translation
- US-003: WebSocket server + session lifecycle
- US-004: Browser frontend (dual-panel display)
- US-005: File upload fallback
- US-006: Evaluation script

## Harness Delta

- Created `docs/product/spec-intake.md` from assignment PDF
- Product contract files to be created: `overview.md`, `architecture.md`, `evaluation.md`
- Architecture decisions to be recorded: D-0006 through D-0009
- Stories to be created: US-001 through US-006
