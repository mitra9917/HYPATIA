# Meta Global AI Developer Hackathon — Research Brief

> Source of truth for event constraints. All HYPATIA decisions must pass these gates.
> Researched from: Cerebral Valley event page, Meta `dev.meta.ai` event + Model API docs, Official Rules coverage, judging rubric screenshots, uploaded software-ideas PDF.

## 1. Event snapshot

| Item | Value |
| --- | --- |
| Name | Meta Global AI Developer Hackathon (Cerebral Valley) |
| Tagline | "Come and build the future of superintelligence." |
| Format | Virtual, worldwide, free if selected |
| Cap | 20,000 accepted applicants |
| Prize pool | **$1,000,000** cash |
| Credits | ~$150 Meta Model API credits per participant; partner credits (Baseten / Modal / Fireworks ~$100 each for select participants) |
| Track for us | **Indie developer track** (students / individual builders) |
| Theme for HYPATIA | **Push the Frontier** (primary) — also narrates "Build for Your World" via Indian schools without labs |

### Key dates (convert carefully)

| Milestone | ET | IST (Asia/Calcutta) |
| --- | --- | --- |
| Kickoff | Oct 26, 2026 | Oct 26 evening IST |
| Workshops / Discord OH | Oct 27 – Nov 4 | ongoing |
| **Submission deadline** | **Nov 4, 2026, 9:00 PM ET** | **Nov 5, 2026, 7:30 AM IST** |
| Judging | Nov 4 – Nov 8 | |
| Closing / live finals | Nov 9, ~12:00 PM ET | Nov 9 evening IST |

**Internal hard target:** submit by **Nov 4, 6:00 PM ET** (Nov 5, 4:30 AM IST) — leave buffer for upload / video processing / form glitches.

### Prize split (Indie track)

| Place | Amount |
| --- | --- |
| 1st | $150,000 |
| 2nd | $100,000 |
| 3rd | $75,000 |
| 4th | $50,000 |
| 5th | $25,000 |
| Bonus pool (viral / community / standouts) | up to $50,000 total across event |

Top ~5 per track → live finals (Stage Three).

## 2. Pass / fail gate (Stage One)

Before any scoring, judges check:

1. Project **reasonably fits** a theme (Build for Your World **or** Push the Frontier).
2. Project **must use Meta Model API and/or Meta open-weight models**.

Fail either → out. No score.

HYPATIA maps to Push the Frontier language almost verbatim:

- give a machine a new capability
- accelerate a scientific experiment
- understand and control a physical system
- models meet the real world

## 3. Scoring rubric (Stage Two) — weights to optimize against

| Category | Weight | What wins |
| --- | --- | --- |
| **Impact** | **30%** | Real user, real number, could become a product, fits theme |
| **Use of Meta AI tooling** | **25%** | Beyond basic integration; "surfaced unexpected capabilities" that surprise judges |
| **Demo** | **25%** | Works live / holds up; demo video is "genuinely cool to watch" |
| **Technical depth & execution** | **20%** | Sound, refined craft — not a fragile toy |

Indie track narrative: creativity, technical ambition, **whether it works**.

## 4. Hackathon rules that can disqualify us

| Rule | Implication for HYPATIA |
| --- | --- |
| **Open source** — repo **must be public** | Public GitHub from day one |
| **Team size** ≤ 4 (solo OK) | Document contributors; one prize representative |
| **Demo shows work built during the hackathon** | Judges must clearly see what was built in-window |
| **New work only** — startups may extend existing products but must **clearly identify** new work | README "Built during hackathon" section + commit timeline |
| **Banned** — illegal / unethical / no rights to code, data, assets | Own test videos; public-domain or licensed clips only; no stolen assets |

Additional ownership note from Official Rules coverage: entrants grant organizers a broad royalty-free license to use/publish/modify submissions; nothing shared is confidential.

## 5. Required / available Meta stack

### Via Meta Model API (`https://api.meta.ai/v1`, OpenAI-compatible)

| Model ID | Role |
| --- | --- |
| `muse-wonder-1.0` | Long-horizon PI agent, sub-agents, computer use |
| `muse-spark-1.3` (+ `-contributor`) | Fast multimodal observer / inner loops; video+image+audio in |
| `muse-image-1.0` | Generate / edit predicted frames; notebook diagrams |
| `muse-voice-transcribe-1.0` | Voice commands during experiments |
| `sam-3.1` | Open-vocab masks + identity-preserving video tracking |

Auth: `MODEL_API_KEY` bearer. Prefer **Responses API** (`POST /v1/responses`) for agents (reasoning replay, tools, files, computer use).

### Open weights (self-host / partner endpoints)

| Model | Role |
| --- | --- |
| Muse Glimmer | Local / cheap hypothesis swarm |
| Muse Spark Open | Optional self-host multimodal fallback |

### Dev tool

| Tool | Role |
| --- | --- |
| Muse Code | Build faster; show multi-agent build log in demo |

### Partners for open-weight inference / sandboxes

- **Baseten** — open-weights + high TPM
- **Modal** — Endpoints + serverless GPUs + **sandboxes** (Toolsmith)
- **Fireworks** — open-weights hosting

## 6. Pricing we must budget against (~$150 credits)

| Resource | Price (approx) |
| --- | --- |
| Muse Spark input / output | $1.25 / $4.25 per 1M tokens (Standard); Contributor much cheaper |
| Muse Wonder input / output | $4 / $20 per 1M tokens (no Contributor on API) |
| Muse Image | $0.01 / image |
| SAM 3.1 video | $0.20 / 1,000 frames (min 50 frames billed per request) |
| SAM 3.1 image | $2.50 / 1,000 images |
| Muse Voice Transcribe | $0.18 / hour audio |

**Cost doctrine:** Wonder only for planning/delegation; Spark (+ Contributor where acceptable) for volume; Glimmer local for swarm; cache SAM results; never re-segment the same clip blindly.

## 7. Submission artifacts checklist

- [ ] Public GitHub repo with clear README
- [ ] Working deployed demo URL (stable for judging window)
- [ ] **≤ 3-minute demo video** (primary judging artifact)
- [ ] Explicit statement of Meta models used
- [ ] Explicit "built during hackathon" / new-work boundary
- [ ] Track selection: Indie
- [ ] Theme: Push the Frontier
- [ ] Optional: public clip for viral / bonus prize

## 8. Official links

- Event: https://cerebralvalley.ai/e/meta-ai-developer-hackathon
- Event details: https://cerebralvalley.ai/e/meta-ai-developer-hackathon/details
- Meta event mirror: https://dev.meta.ai/events/global-hackathon
- Model API overview: https://dev.meta.ai/docs/overview
- Pricing: https://dev.meta.ai/docs/pricing-rate-limits
- Computer use: https://dev.meta.ai/docs/computer-use
- SAM: https://dev.meta.ai/docs/sam/overview
