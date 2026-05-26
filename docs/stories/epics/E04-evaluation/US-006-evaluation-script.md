# US-006 Evaluation Script

## Status

planned

## Lane

normal

## Product Contract

`scripts/evaluate.py` runs the full pipeline against a sample audio file with a known ground-truth transcript and prints a report: WER, entity preservation %, average/max latency, and projected cost for a 2-hour session.

## Relevant Product Docs

- `docs/product/evaluation.md`

## Acceptance Criteria

- `python scripts/evaluate.py --audio sample_audio/sample.mp3 --ground-truth sample_audio/ground_truth.txt` runs without error.
- Report prints WER as a percentage.
- Report prints entity preservation rate (entities found in translation / entities in source).
- Report prints avg and max latency per chunk in seconds.
- Report prints actual API cost and projected 2h cost.
- All four assignment targets are checked (pass/fail) against targets.

## Design Notes

- `jiwer` library for WER calculation
- Entity extraction: same logic as `domain/entities.py`
- Cost calculation: count Whisper audio seconds + Claude input/output tokens from API responses
- Ground truth format: plain text, one sentence per line

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | n/a |
| Integration | n/a |
| E2E | Run script → report printed with all four metrics |
| Platform | Manual |
| Release | Report output included in submission README |

## Harness Delta

None expected.

## Evidence

_Not yet implemented._
