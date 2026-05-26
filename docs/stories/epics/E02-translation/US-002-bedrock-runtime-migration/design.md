# Design - US-002 Bedrock Runtime Migration

## Domain Model

No domain contract change. `TranslationResult` continues to contain translated
text, token usage and a structured provider error.

## Application Flow

`InterpretSession` sends extracted transcript and entity memory to
`ClaudeClient`. `ClaudeClient` sends an Anthropic Messages payload through
Bedrock Runtime and maps the response back to `TranslationResult`.

## Interface Contract

Internal provider configuration:

- `AWS_REGION` or `AWS_DEFAULT_REGION`: Bedrock region.
- Standard AWS credential chain, including `AWS_PROFILE` for local execution.
- `BEDROCK_CLAUDE_MODEL_ID`: optional model/profile override.

Verified inference profile ID:
`global.anthropic.claude-haiku-4-5-20251001-v1:0` in `ap-northeast-2`.

## Data Model

No persistent data or migration.

## UI / Platform Impact

No browser contract change. A Bedrock permission or provider error is surfaced
through the existing result error path.

## Observability

Provider failures are tagged `bedrock_claude_error` at the boundary.

## Alternatives Considered

1. Direct Anthropic API with an Anthropic key.
2. A different Bedrock-hosted model.
3. Bedrock Converse API.
