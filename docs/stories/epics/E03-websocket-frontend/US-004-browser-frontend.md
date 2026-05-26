# US-004 Browser Frontend — Dual-Panel Display

## Status

planned

## Lane

normal

## Product Contract

Single HTML file. User opens it in a browser, clicks Start, grants mic access. Audio is captured in 2500ms chunks and sent via WebSocket. Translations display in real-time in a dual-panel layout. Language direction can be toggled. Latency badge shows lag behind speaker.

## Relevant Product Docs

- `docs/product/overview.md`
- `docs/decisions/0009-frontend-approach.md`

## Acceptance Criteria

- Page loads and displays Start button without any server connection.
- Clicking Start requests mic permission and opens WebSocket to `ws://localhost:8000/ws/interpret`.
- Audio captured via `MediaRecorder` at 2500ms `timeslice`, sends each blob as binary WebSocket frame.
- Left panel shows original language transcript, right panel shows translation. Both scroll as text accumulates.
- Language toggle cycles: Auto → EN→VI → VI→EN.
- Latency badge updates per chunk: `"1.4s behind speaker"`.
- On WebSocket error or disconnect: show error banner, Stop button resets state.
- Works without any npm install or build step — open `index.html` directly.

## Design Notes

- Single file: `surfaces/browser/index.html`
- No external JS dependencies (no CDN)
- WebSocket binary send: `ws.send(blob)` directly from `ondataavailable`
- Config frame sent on language toggle: `ws.send(JSON.stringify({action: "set_language", direction: "..."}))`
- UI layout: two equal-width panels, monospace font, auto-scroll to bottom

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | n/a — single HTML file, logic minimal |
| Integration | n/a |
| E2E | Manual: open file, speak, observe dual-panel updating within 3s |
| Platform | Manual: Chrome + Edge |
| Release | Demo video in submission |

## Harness Delta

None expected.

## Evidence

_Not yet implemented._
