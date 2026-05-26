# 0010 Claude Haiku Access Path - Amazon Bedrock Runtime

Date: 2026-05-26

## Status

Accepted

## Context

The translation model remains Claude Haiku 4.5, but the project must invoke it
through Amazon Bedrock instead of the direct Anthropic API. This changes
credentials, model identifiers, runtime failures, regional access, and cost
verification.

## Decision

Use Amazon Bedrock Runtime `InvokeModel` for translation, with the Bedrock
Messages request shape and the Global inference profile ID
`global.anthropic.claude-haiku-4-5-20251001-v1:0`.

Configuration is supplied through the standard AWS credential chain,
`AWS_REGION`, and optional `BEDROCK_CLAUDE_MODEL_ID` override. In
`ap-northeast-2`, Claude Haiku 4.5 is exposed through an inference profile,
rather than direct on-demand foundation-model invocation.

## Alternatives Considered

1. Continue calling Anthropic directly with `ANTHROPIC_API_KEY`; rejected by the selected provider requirement.
2. Use a different Bedrock translation model; rejected because it would also alter the accepted Claude Haiku model contract.
3. Use the Bedrock Converse API; viable later, but `InvokeModel` directly maps to the accepted Claude Messages contract with a minimal code change.

## Consequences

Positive:

- Claude traffic and authentication are governed through AWS Bedrock access.
- Translation behavior and the system prompt remain unchanged.

Tradeoffs:

- Deployments must provision Bedrock model access and AWS credentials.
- Available model/profile IDs and pricing must be verified for the selected AWS region.

## Follow-Up

- Recalculate the cost estimate using the deployed region and inference profile.
