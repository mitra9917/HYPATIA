# SAM decode — Playbook #19 / issue #51

## Server-side (default)

HYPATIA decodes SAM 3.1 **Responses API** output with **`meta_sam_parser`** in the API:

| Module | Role |
| --- | --- |
| `hypatia/sam_live.py` | `stream=True` video call; video **before** text in content |
| `hypatia/sam_parser_bridge.py` | `VideoSegmentationSnapshot` → `Track.mask_frames[]` |
| `hypatia/sam_decode.py` | Parser first, legacy JSON fallback |

The web lab renders **`bbox_norm`** (0–1) from the session JSON in `TrackOverlay` — no PNG mask upload required for demo.

## Client-side (optional stretch)

**`@meta-sam/parser`** in `apps/web` is optional for streaming masks directly in the browser without shipping full mask RLE on every poll. We use **server overlay JSON** until bundle size / SSE mask streaming is needed (issue #51 optional bullet).

## Fixtures

- `data/fixtures/sam/pendulum_boxes.json` — box records for unit tests without Meta
- Live path still falls back to **hybrid** synthesis if API returns undecodable text

## Meta call shape

```text
POST /v1/responses  stream=true
model: sam-3.1
input: [ input_video(file_id), input_text(prompt) ]
→ meta_sam_parser video_segmentation_format
```

Without `file_id`, SAM 3 rejects the request (`input_video` required).
