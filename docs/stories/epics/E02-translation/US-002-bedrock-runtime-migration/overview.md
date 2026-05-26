# Overview - US-002 Bedrock Runtime Migration

## Current Behavior

`ClaudeClient` calls the direct Anthropic Messages API using
`ANTHROPIC_API_KEY`.

## Target Behavior

Translation uses Claude Haiku 4.5 through Amazon Bedrock Runtime while keeping
the prompt, session entity memory, and `TranslationResult` contract stable.

## Affected Users

- Operators configuring the localhost POC.
- Meeting participants relying on translated output.

## Affected Product Docs

- `docs/product/spec-intake.md`
- `docs/product/architecture.md`
- `docs/product/evaluation.md`
- `docs/stories/epics/E02-translation/US-002-entity-memory-translation.md`

## Non-Goals

- Changing the speech-to-text provider.
- Adding TTS.
- Replacing Claude Haiku with another translation model.
