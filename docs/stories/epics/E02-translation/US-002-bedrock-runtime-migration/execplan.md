# Exec Plan - US-002 Bedrock Runtime Migration

## Goal

Run Claude Haiku translation through Amazon Bedrock Runtime without altering
the interpreter's user-visible text flow.

## Scope

In scope:

- Bedrock provider client configuration and request mapping.
- Tests for the provider boundary.
- Product and decision documentation updates.

Out of scope:

- TTS or new interface behavior.
- Live credential provisioning.
- Changes to Whisper STT.

## Risk Classification

Risk flags:

- External systems.
- Existing behavior.
- Weak proof until a credentialed Bedrock call is run.

Hard gates:

- External provider behavior.

## Work Phases

1. Confirm supported Bedrock Claude Haiku model ID.
2. Record provider access-path decision.
3. Replace provider boundary implementation and configuration.
4. Run deterministic tests.
5. Record remaining credentialed validation requirement.

## Stop Conditions

Pause for human confirmation if the selected AWS account cannot access Claude
Haiku and a different model would be required.
