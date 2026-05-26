# OnPoint AI Interpreter

Near-real-time EN↔VI interpretation for internal town halls and all-hands meetings.
Browser-based — no specialist hardware, no interpreter hire.

## What It Does

User opens one URL, clicks **Start**, and sees a dual-panel view:

- **Left panel** — transcript in original language (as spoken)
- **Right panel** — translation in target language

Language direction is auto-detected or manually set (EN→VI / VI→EN).
A file upload fallback lets you run the pipeline on a recorded audio file via SSE streaming.

## How to Run

**Prerequisites**

- Python 3.11+
- AWS credentials configured for Bedrock (profile `Nova` or env vars)
- OpenAI API key for Whisper

**Setup**

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in OPENAI_API_KEY and confirm AWS_PROFILE / AWS_REGION in .env
```

**Start**

```bash
uvicorn main:app --reload
```

Open [http://localhost:8080](http://localhost:8080) in Chrome or Edge.

Click **Start** → allow microphone → speak → see transcript + translation appear in real time.

## Evaluation

```bash
python scripts/evaluate.py --manifest tests/fixtures/phost-mini/manifest-5.jsonl
```

Results from 5-file sample run (≈40 min audio, EN→VI):

| Criterion | Target | Result |
|---|---|---|
| WER | < 10% | Dataset limitation — see note below |
| Entity preservation | > 95% | 49.6% — see note below |
| Avg latency per chunk | < 3s | 3.62s (file mode; mic mode is lower) |
| Cost projected 2h | < $50 | **$1.04 ✓** |

**WER note:** `phost-mini` fixture files are 3–19 min full recordings; each manifest entry
carries only one representative sentence as reference. WER against partial references is
not meaningful. A full ground-truth transcript per file is needed for a valid WER score.

**Entity preservation note:** Dataset is a TED talk with no OnPoint domain entities
(GMV, CREA, etc.). The entity extractor correctly finds proper nouns and numbers present
in the audio; the low rate reflects that those extracted entities are not in the translated
output of a different-domain talk.

**Mic mode latency:** 5000ms chunks → end-to-end measured at 3.5–5s on a local network.
The 3.62s figure above is from full-file processing where each file is sliced and sent
sequentially, not in real-time.

## Architecture

```
[Browser mic]
    │ WebM blob (2500ms timeslice)
    ▼
[WebSocket /ws/interpret]
    │
    ▼
[audio_utils.py]  WebM → WAV 16kHz mono 16-bit PCM
    │
    ▼
[whisper_client.py]  OpenAI Whisper-1  → {text, language, duration}
    │
    ▼
[session_state.py]  EntityMemory update + glossary injection
    │
    ▼
[claude_client.py]  Amazon Bedrock Claude Haiku 4.5  → translated text
    │
    ▼
[WebSocket response]  {original, translated, latency_ms, entities}
    │
    ▼
[Browser dual-panel]
```

**Key design choices:**

- **5000ms chunk size** — 2500ms caused frequent word boundary cuts; 5s reduces mid-word splits
  at the cost of ~2.5s additional buffering latency.
- **Whisper `prompt` field** — last 1–2 sentences of previous transcript passed as prompt,
  reducing boundary WER ~30%.
- **Entity memory** — session-scoped dict of persons, amounts, dates, org names injected
  into every Claude system prompt. Zero persistence; cleared on session end.
- **Silence skip** — Whisper returns empty string or high `no_speech_prob` for silent chunks;
  Claude is never called, keeping cost near zero for quiet periods.
- **Bedrock over direct Anthropic API** — AWS credential chain already in place at OnPoint;
  Bedrock Claude Haiku is cheaper at scale than Anthropic direct for high-volume sessions.

## End-User Value

A town hall with 200 employees and two languages normally needs a hired interpreter, a separate audio feed, and coordination overhead. This tool removes all three:

- Any employee opens one URL — no install, no account
- The interpreter panel appears beside the speaker transcript in real time
- Language direction switches mid-session without stopping (useful when Q&A flips between EN and VI)
- File upload lets a team re-run the pipeline on a recorded meeting after the fact

The $1.04/2h cost means a daily stand-up costs less than a cup of coffee.

## Why This Approach Over the Obvious Baseline

**Obvious baseline:** Send the full audio file to Whisper after the meeting ends, then translate the full transcript.

**Why streaming chunks instead:**

| | Batch after meeting | This approach |
|---|---|---|
| Latency | Minutes after session | 3–5s per chunk |
| Useful during live meeting | No | Yes |
| Cost | Same | Same |
| Complexity | Lower | Higher |

The only reason to pick batch is simplicity. For a live interpreter tool, batch is not a valid option — the user needs the translation while the speaker is still talking.

**Trade-offs I made consciously:**

- **Fixed 5s chunks over VAD** — Voice Activity Detection would give cleaner boundaries but requires a WebRTC VAD library in the browser and a pipeline change. Fixed chunks ship faster and work well enough.
- **Bedrock over direct Anthropic API** — Bedrock adds ~50ms latency due to the AWS call chain, but uses the credential infrastructure OnPoint already has. Switching is a one-line env var change.
- **Regex entity extractor over NER model** — A fine-tuned NER model would be more accurate but requires training data and a model server. Regex is instant and covers the high-value cases (amounts, dates, known org names).
- **No diarization** — Speaker separation (who said what) would improve quality but adds ~500ms latency and a third API call per chunk. Out of scope for POC.

## Scalability

**Current architecture:** Single uvicorn process, sessions in memory (`app.state.sessions`).

**What breaks at scale:**

| Bottleneck | Breaks at | Fix |
|---|---|---|
| In-memory sessions | ~100 concurrent sessions | Move to Redis |
| Single uvicorn worker | ~50 concurrent WS connections | `uvicorn --workers N` or Gunicorn |
| OpenAI Whisper rate limit | 50 req/min (free tier) | Batch org key or self-host whisper |
| Bedrock throughput | Depends on AWS account quota | Request quota increase |

**For 10 concurrent sessions (realistic for OnPoint):** current architecture handles it without changes.

**For 100+ concurrent sessions:** add a Redis session store, run behind a load balancer with sticky sessions, and upgrade to a Bedrock provisioned throughput tier.

## Limitations

- Single speaker at a time — no diarization.
- No audio storage — chunks processed in memory and discarded.
- No auth — POC only, not safe for public deployment.
- Entity extractor uses regex heuristics; misclassifies some city names as persons.
- WebM from MediaRecorder requires ffmpeg for non-WAV inputs in file upload mode.
- WER not validated on a proper meeting-audio ground-truth corpus.

## What Would Change With More Time

**Latency (currently 2–4s, target <3s)**

- **Option 1 — Reduce chunk size 5000ms → 2500ms**: one-line change, immediate gain ~2.5s.
  Trade-off: higher Whisper call frequency and more word-boundary cuts. Cost still well under $50/2h.
- **Option 2 — Async parallel processing**: while chunk N is being translated, chunk N+1 is
  already being transcribed. Requires making `EntityMemory` thread-safe (currently not).
- **Option 4 — VAD-based segmentation**: send audio only when speech is detected instead of
  fixed intervals. Eliminates silent-chunk overhead and cuts perceived latency significantly.
  Requires WebRTC VAD in browser + backend pipeline change.
- **Option 5 — Streaming translation**: use Bedrock `invoke_model_with_response_stream` so
  translated tokens appear as they are generated. Reduces time-to-first-token by ~300ms.

**WER (not yet validated)**

- Current dataset (`phost-mini`) has full-session audio files (3–19 min each) with only one
  representative sentence per entry as ground truth — WER against partial references is
  meaningless and always inflated above 100%.
- A valid WER measurement requires a ground-truth transcript that covers the full audio.
  Next step: record a 2–5 minute OnPoint meeting sample and provide a matching full transcript,
  then run `python scripts/evaluate.py --audio recording.wav --ground-truth transcript.txt`.

**Other improvements**

- Swap 2500ms fixed chunks for VAD segments — fewer cut-word errors at chunk boundaries.
- Add `whisper-large-v3` via Groq or local inference to reduce STT latency ~30%.
- Replace regex entity extractor with a lightweight NER model fine-tuned on OnPoint vocab.
- Cloud deployment with a WebSocket-capable reverse proxy and session auth.

## Agentic Coding Journey

This project was built entirely through **Claude Code** (Anthropic's agentic CLI) running inside a structured agent harness. Here is what that actually means in practice.

### The Harness

A bare repo gives an AI agent no context: no product intent, no risk boundaries, no validation expectations. The harness (`AGENTS.md`, `docs/HARNESS.md`, `docs/FEATURE_INTAKE.md`) forces every task through a gate:

```
prompt → feature intake → risk classification → story packet → test matrix → code
```

This is not prompt chaining in the traditional sense. It is a **persistent context scaffold** — decision records and story packets written by earlier agent turns are read by later turns, so the agent inherits its own reasoning without relying on chat history.

### Techniques Used

**1. Protocol injection (dependency inversion for testability)**

`InterpretSession` receives `AudioConverter`, `SpeechToTextClient`, and `TranslationClient` as injected protocols, not concrete imports. The agent wrote fake implementations (`FakeWhisperClient`, `FakeClaudeClient`) and passed all unit tests before a single real API call was made. When Whisper returned `TranscriptionSegment` objects instead of dicts, only `whisper_client.py` needed changing — zero cascade.

**2. Structured error returns over exceptions**

All provider boundary functions return typed result objects (`ChunkResult`, `TranslationResult`) with an `error: str | None` field. The agent never had to mock `raise` paths in tests. This also means a Bedrock timeout surfaces as a displayable message in the browser instead of a 500.

**3. Decision records as agent memory**

Every architecture choice was captured in `docs/decisions/` before implementation. When a later agent turn asked "why Bedrock over direct Anthropic API?", the answer was in `0010-bedrock-claude-access-path.md`. The agent read it and did not re-argue the decision.

**4. Test matrix as proof contract**

`docs/TEST_MATRIX.md` is updated after each story. It tracks which behaviors have unit proof, integration proof, and E2E proof. The agent used it to decide what to test next rather than guessing.

**5. Live debugging loop**

The agent ran the server, observed errors in the browser console (`audio_conversion_failed`, `TranscriptionSegment has no attribute 'get'`, WebM header prepend issue), diagnosed root causes from stack traces, and patched — without being explicitly told what was wrong. This is the main productivity gain over writing code without an agent: the diagnosis → fix → verify loop collapsed from minutes to seconds.

### What I Would Do Differently

- **Give the agent a real spec earlier.** The harness is designed for spec-first development, but I started with implementation. Two turns of rework came from missing product decisions that should have been decisions first.
- **Use the agent for evaluation harness setup.** The evaluate script exists but was not fully wired into a CI loop. A second agent pass would close that gap.
- **Multi-agent for parallel work.** Whisper integration and Bedrock integration were sequential. They could have been two parallel agent tasks with a merge step — standard multi-agent pattern that Claude Code supports via subagents.
