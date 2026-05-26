# Evaluation Contract

## Required Targets (from assignment)

| Criterion | Target | Measurement method |
| --- | --- | --- |
| Transcription WER | < 10% | `scripts/evaluate.py` vs ground truth transcript |
| Key entity preservation | > 95% | Entity match rate: numbers, dates, names, amounts |
| Latency behind speaker | < 3 seconds | Timestamp delta: chunk end → translation rendered |
| Cost per 2-hour session | < $50 | Whisper minutes × $0.006 + Bedrock Claude Haiku tokens at the selected region's rate |

## Proposed Additional Criteria

| Criterion | Target | Reason |
| --- | --- | --- |
| Empty chunk skip rate | 100% | Silence/noise chunks must not call Claude — cost waste |
| Chunk processing success rate | > 99% | Dropped chunks break speaker flow |
| Session startup time | < 5 seconds | From click Start to first translation |

## Cost Estimate (2h session)

| Component | Volume | Unit cost | Total |
| --- | --- | --- | --- |
| Whisper API | 120 min | $0.006/min | $0.72 |
| Bedrock Claude Haiku input | ~180k tokens | Confirm for selected AWS region/profile | TBD |
| Bedrock Claude Haiku output | ~90k tokens | Confirm for selected AWS region/profile | TBD |
| **Total** | | | **TBD after Bedrock regional pricing check** |

Recompute the total after confirming Bedrock pricing for the selected region and inference profile.

## Evaluation Script Output Format

```
=== AI Interpreter Evaluation Report ===
Audio file   : sample_meeting.mp3
Duration     : 4m 32s

STT
  WER                  : 7.3%
  Chunks processed     : 109
  Empty chunks skipped : 4

Translation
  Entity preservation  : 97.2%
  Avg latency          : 1.84s
  Max latency          : 2.61s

Cost
  Whisper              : $0.027
  Bedrock Claude Haiku : $TBD
  Total                : $0.035
  Projected 2h session : $0.46
```
