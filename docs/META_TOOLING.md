# Meta Tooling Map — Maximize the 25% Rubric

Judges explicitly reward going **beyond a basic chatbot integration** and surfacing capabilities that **"surprised even us."**  
Rule for HYPATIA: **every Meta tool below is load-bearing**. If we can remove it and the product still works the same, we are failing this category.

## 1. Inventory (must appear in README + demo narration)

| Tool | Model ID / surface | HYPATIA job | Demo beat if removed |
| --- | --- | --- | --- |
| **Muse Spark 1.3** | `muse-spark-1.3` (+ contributor) | Observer: video understanding → objects, variables, SAM prompts, plain-language narration | Cannot open-vocab a never-seen scene |
| **Muse Wonder** | `muse-wonder-1.0` | Principal Investigator: long-horizon campaign, sub-agents, Toolsmith, Experiment Designer, computer use | No autonomy / no self-tooling / no experiment design |
| **Muse Image** | `muse-image-1.0` | Imagination: predicted future frame + notebook apparatus diagrams | No visual falsifiable prediction (no ghost) |
| **SAM 3.1** | `sam-3.1` | Scientific instrument: masks, tracking, SI measurements; audits imagined frames | No numbers → no science |
| **Muse Glimmer** | open weights (Modal/Baseten/local) | Offline hypothesis swarm; privacy/cost story; stretch fine-tune on accept/reject laws | Cost explodes; no open-weights story |
| **Muse Voice Transcribe** | `muse-voice-transcribe-1.0` | Hands-free: "what if heavier bob?" while hands are on the apparatus | Breaks live experiment UX |
| **Muse Code** | CLI / agent | Build velocity; show build log in video as process proof | Slower; weaker "built with Meta" authenticity |
| **Muse Spark Open** (optional) | self-host / partner | Fallback multimodal if API constrained | Nice-to-have resilience |

## 2. Four "unexpected capabilities" (name these on screen)

These are the money lines for Tooling + Demo:

1. **SAM 3.1 as a scientific ruler** — not "segment a dog," but metres, angles, doubling times.
2. **SAM grades Muse Image** — image generation becomes a *falsifiable prediction*, not a pretty picture.
3. **Muse Wonder as Principal Investigator** — writes its own instruments (Toolsmith) and designs experiments by information gain.
4. **Glimmer as offline hypothesis swarm** — open weights doing bulk science cheaply / privately.

## 3. Call patterns (implementation contracts)

### 3.1 Observer — Muse Spark (video)

```text
POST /v1/responses
model: muse-spark-1.3
input: [ instruction, input_video(file_id) ]
text.format: json_schema(SceneBrief)
reasoning.effort: medium
```

Output must include `sam_prompts[]` used verbatim by Measurer.

### 3.2 Measurer — SAM 3.1 (video track)

```text
POST /v1/responses  stream=true
model: sam-3.1
input: [ input_text("pendulum bob"), input_video(file_id) ]
→ meta_sam_parser → per-frame boxes/masks with stable IDs
```

Then OpenCV moments / PCA angle / known-object scale → SI trajectories.

**Cost tip:** upload once via Files API; reuse `file_id`. Prefer 10–15 fps scientific clips over 60 fps waste. Cache tracks under `data/fixtures/`.

### 3.3 PI — Muse Wonder

```text
model: muse-wonder-1.0
tools: [spawn_theorist, run_pysr, request_experiment, run_toolsmith, library_search, computer?]
reasoning.effort: high
previous_response_id: <campaign continuity>
```

Wonder plans; Spark/Glimmer execute sub-tasks. Never put bulk equation search on Wonder.

### 3.4 Imagination — Muse Image

Preferred path: **image edit** of current frame with mask hint of moving object + text: "move the bob to angle θ predicted by law B at t+Δ".

Fallback: generate apparatus diagram for notebook only; geometric renderer draws the live ghost.

### 3.5 Audit — SAM on imagined vs real

Segment the same object in both frames → centroid / mask IoU / trajectory residual → score.

### 3.6 Voice — Muse Voice Transcribe

Realtime WS `wss://api.meta.ai/v1/asr/realtime` for live demo; file transcription for recorded Q&A.

### 3.7 Computer use (stretch)

Wonder + native computer tool against a browser running PhET pendulum: change length, release, read on-screen period. Proves "act" without custom hardware.

### 3.8 Muse Code (process)

Use for scaffolding agents, tests, UI. Capture a 10–15s screen recording of Muse Code committing a Toolsmith test — put in demo B-roll.

## 4. Cost routing matrix

| Workload | Model | Why |
| --- | --- | --- |
| Scene understanding bursts | Spark Contributor (if OK) / Spark | Cheap multimodal |
| PI plan once per session | Wonder | Capability |
| Rival theorist drafts | Glimmer local | Volume |
| Fit + score | PySR / SciPy (no LLM) | Maths decides |
| Ghost frames (few) | Muse Image | $0.01 each — budget ~50–100 for demo/evals |
| Tracking | SAM video | $0.20 / 1k frames — biggest silent cost |
| Voice during live demo | Voice Transcribe | Negligible at $0.18/hr |

**Budget envelope (target):** stay inside ~$150 API credits for build+evals+demo with fixtures covering the live path.

## 5. Evidence pack for judges (README section)

**Canonical table:** [`docs/META_EVIDENCE.md`](./META_EVIDENCE.md) (paths + demo timestamps).  
**Machine-readable:** [`meta_evidence.json`](../meta_evidence.json).

| Capability | Meta tool | File / module | Demo timestamp |
| --- | --- | --- | --- |
| Open-vocab measure | SAM 3.1 | `services/api/hypatia/measurer.py` | 0:15–0:45 |
| Rival theories + next experiment | Wonder | `services/api/hypatia/pi.py` | 0:45–1:15 |
| Ghost imagination | Muse Image + SAM audit | `services/api/hypatia/pipeline.py` | 1:15–1:45 |
| New domain zero new code | Spark Observer + Toolsmith | `domains/cells.py`, toolsmith | 1:45–2:15 |
| Physics watermark | VERITAS module | `services/api/hypatia/veritas.py` | 2:15–2:35 |
| Self-improve | Law/tool library | `GET /api/library/laws`, `/api/library/tools` | 2:35–2:50 |
| Built with Muse Code | process | `demo/` B-roll | credits |

## 6. Anti-patterns (do not do)

- Single Spark chat that "explains the video" without SAM measurements
- Muse Image used only for a logo / landing hero
- Wonder called on every keystroke
- Claiming open-weights usage without actually running Glimmer
- Hiding that math (PySR), not the LLM, accepts the law — be honest; judges like craft
