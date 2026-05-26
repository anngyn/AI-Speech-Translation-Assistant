# 0007 Translation Model — Claude Haiku vs GPT-4o-mini

Date: 2026-05-26

## Status

Accepted

## Context

Need a fast, cheap LLM for translation with entity-preservation constraints. Two main candidates: Anthropic Claude Haiku and OpenAI GPT-4o-mini.

## Decision

Use Anthropic Claude Haiku (`claude-haiku-4-5-20251001`).

## Alternatives Considered

1. **GPT-4o-mini** — similar cost, good translation quality, but system prompt entity injection less reliable in testing; would require same OpenAI account as Whisper anyway.
2. **DeepL API** — purpose-built translation, excellent quality, but no system prompt for entity injection. Cannot enforce "preserve '150 tỷ' exactly" constraint. Entity preservation would fail.
3. **Claude Sonnet** — better quality but 5× more expensive. Overkill for translation task.

## Decision Rationale

Claude Haiku chosen because:
- System prompt injection for entity memory is natural and reliable
- `<3s` latency for translation step (typically 300-500ms)
- Cost: ~$0.25/1M input tokens — translation adds ~$0.15 to a 2h session
- Assignment context: demonstrating Claude use is relevant to OnPoint AI team

## Consequences

Positive:
- Entity preservation constraint enforced via system prompt
- Low latency, low cost
- Claude usage aligns with assignment's "agentic coding journey" ask

Tradeoffs:
- Two different providers (OpenAI for Whisper, Amazon Bedrock for Claude translation) require separate credentials
- If the configured Bedrock model/region is unavailable, fallback is needed

## Follow-Up

- Access path moved to Amazon Bedrock Runtime in `docs/decisions/0010-bedrock-claude-access-path.md`; this decision remains the model-selection rationale.
- If single-provider preferred: GPT-4o-mini is drop-in replacement
- Consider Claude Haiku 4.5 model ID update if newer version releases
