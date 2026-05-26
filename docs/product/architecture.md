# Architecture — AI Interpreter

## Data Flow

```
[Browser mic]
    │ MediaRecorder blob (audio/webm, 2500ms timeslice)
    ▼
[WebSocket client]
    │ binary frame
    ▼
[FastAPI WebSocket endpoint]  ws_handler.py
    │
    ▼
[audio_utils.py]
    WebM bytes → pydub AudioSegment → WAV (16kHz, mono, 16-bit PCM)
    │
    ▼
[whisper_client.py]
    POST /v1/audio/transcriptions
    model=whisper-1, language=None (auto-detect), prompt=last_transcript
    → {text, language, duration}
    │
    ▼
[session_state.py]
    update EntityMemory {persons, amounts, dates, org_names}
    build translation system prompt with entity list + OnPoint glossary
    │
    ▼
[claude_client.py]
    Amazon Bedrock Runtime: Anthropic Claude Haiku 4.5
    system=<context prompt>, user=<transcript>
    → translated text
    │
    ▼
[WebSocket response]
    {original, translated, language, latency_ms, entities}
    │
    ▼
[Browser dual-panel display]
```

## Component Boundaries

| Component | Responsibility | Must not |
| --- | --- | --- |
| `audio_utils.py` | Format conversion only | Know about sessions or translation |
| `whisper_client.py` | STT API call + error handling | Know about entity memory |
| `claude_client.py` | Bedrock Claude translation call + prompt assembly | Know about audio or sessions |
| `session_state.py` | Entity memory, glossary, session config | Call any external API |
| `interpret_session.py` | Orchestrate STT → state → translate | Directly call provider APIs |
| `ws_handler.py` | WebSocket lifecycle, session creation | Contain business logic |

## Key Design Decisions

### Chunk size: 2500ms
Shorter (1s) → more Whisper calls, higher cost, worse word boundary accuracy.
Longer (5s) → latency exceeds 3s target.
2500ms balances latency and accuracy.

### Overlap buffer: 500ms
Last 500ms of chunk N prepended to chunk N+1.
Prevents entity truncation at chunk boundaries.
Backend deduplicates the overlap in transcript stitching.

### Whisper `prompt` field
Pass last 1-2 sentences of previous transcript as Whisper prompt.
Gives Whisper context → reduces WER at chunk boundary by ~30%.

### Entity memory: session-scoped in-memory dict
No DB, no persistence. Session ends → memory cleared.
Entity memory grows across chunks within a session.
Injected into every Claude system prompt call.

### Silence detection: skip empty transcript
Whisper returns `""` or whitespace-only for silence.
Skip Claude call entirely → zero cost for silent chunks.

## File Structure

```
D:/An/Project/OnPoint/
├── main.py                          # FastAPI app, mounts router
├── app/
│   ├── domain/
│   │   ├── entities.py              # EntityMemory, ChunkResult, TranslationResult
│   │   └── glossary.py              # OnPoint domain term seed list
│   ├── application/
│   │   ├── interpret_session.py     # STT → memory → translate orchestrator
│   │   └── session_state.py         # Session entity memory + config
│   ├── infrastructure/
│   │   ├── audio_utils.py           # WebM → WAV conversion
│   │   ├── whisper_client.py        # OpenAI Whisper API wrapper
│   │   └── claude_client.py         # Amazon Bedrock Claude Haiku wrapper
│   └── interface/
│       ├── ws_handler.py            # WebSocket endpoint + session lifecycle
│       └── audio_router.py          # REST file upload endpoint (fallback demo)
├── surfaces/
│   └── browser/
│       └── index.html               # Single-file frontend
├── scripts/
│   ├── evaluate.py                  # WER + latency + cost report
│   └── sample_audio/                # Test fixtures
├── requirements.txt
└── .env.example
```

## Dependency Rule

```
domain ← application ← infrastructure ← interface ← surfaces
```

`domain` and `application` must not import from `infrastructure` directly.
`interpret_session.py` receives injected clients — no direct provider imports.
