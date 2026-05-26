# 0009 Frontend Approach — Vanilla HTML vs Framework

Date: 2026-05-26

## Status

Accepted

## Context

POC needs a browser UI for audio capture and real-time display. Must be demo-ready without build tooling.

## Decision

Single-file vanilla HTML/JS (`surfaces/browser/index.html`).

## Alternatives Considered

1. **React + Vite** — better component model but requires Node.js, npm install, build step. Friction for non-technical stakeholder demo.
2. **Svelte** — lighter than React, still needs build step.
3. **HTMX** — good for server-rendered updates but WebSocket binary audio streaming is awkward.

## Consequences

Positive:
- Open `index.html` directly in browser — zero setup for demo
- `MediaRecorder` API and `WebSocket` are native browser APIs, no lib needed
- Non-technical stakeholder can run demo independently

Tradeoffs:
- No component reuse, inline styles
- Not scalable beyond POC — acceptable for assignment scope

## Follow-Up

- If productionized: migrate to React or Svelte with proper component structure
