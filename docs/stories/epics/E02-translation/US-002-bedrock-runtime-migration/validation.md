# Validation - US-002 Bedrock Runtime Migration

## Proof Strategy

Deterministic tests prove the Bedrock Messages payload and response mapping.
Final provider proof additionally requires AWS credentials with access to
Claude Haiku in the configured region.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Bedrock payload includes model, messages version and prompt; provider errors map to result errors |
| Integration | Credentialed Bedrock call preserves `Q1` and `150` in an EN translation |
| E2E | Existing microphone/upload flow returns displayed translations through Bedrock |
| Platform | Operator configures AWS credential chain and selected Bedrock region |
| Performance | Measure translation latency in evaluation report |
| Logs/Audit | Existing structured error result carries `bedrock_claude_error` |

## Fixtures

- Fake Bedrock Runtime JSON response for deterministic tests.
- Sample Vietnamese transcript containing `Q1` and `150 ty`.

## Commands

```text
python -m pytest
python scripts/evaluate.py --audio <sample> --ground-truth <transcript>
```

## Acceptance Evidence

- `python -m compileall -q app tests scripts main.py`: passed on 2026-05-26.
- `tests/test_claude_client.py`: two Bedrock boundary cases passed through isolated function execution on 2026-05-26.
- Existing entity-memory and interpreter-session unit functions: four cases passed on 2026-05-26.
- `.venv/bin/python -m pytest -q`: passed, six tests, on 2026-05-26.
- FastAPI app import through `.venv`: passed on 2026-05-26.
- Credentialed Bedrock validation passed on 2026-05-26 using AWS profile `Nova`, region `ap-northeast-2`, and inference profile `global.anthropic.claude-haiku-4-5-20251001-v1:0`; output preserved `Q1` and `150`.
- OpenAI Whisper authentication probe with a generated WAV reached the API successfully on 2026-05-26.
- Pending: browser/evaluation validation with representative meeting audio.
