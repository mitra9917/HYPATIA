# Voice realtime ASR (Playbook #49 / issue #61)

Live mic streaming targets Meta **`wss://api.meta.ai/v1/asr/realtime`** (`META_TOOLING.md` §3.6).

## Shipped in HYPATIA

- **WebSocket:** `GET /api/voice/realtime` (upgrade) — streams `ready`, `partial`, `final`, `reply` JSON events.
- **Fallback:** `POST /api/voice/turn` with `transcript` or `audio_base64` (Playbook #43 / #32).
- **UI:** Voice button tries WebSocket first, then HTTP turn on failure.

When `MODEL_API_KEY` is absent, the socket uses a **fixture stream** so judges can demo without live ASR.
