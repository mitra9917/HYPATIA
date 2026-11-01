# Winning Strategy — Indie Track Global Finals

Goal: clear Stage One, top-5 score into Stage Three live finals, then win on the same rubric with a cold demo that never fails.

## 1. Rubric attack plan

### Impact (30%) — lead with a real number

- Hook: **~1.25 lakh Indian secondary schools without an integrated science lab** → phone becomes the lab.
- Secondary: researchers drowning in video; reproducibility crisis; world-model training data.
- Product path slide: free student app → research notebook → law-labeled video API.
- Do **not** overclaim medical/legal outcomes. Stay scientific-assistant honest.

### Use of Meta AI tooling (25%) — surprise, don't checklist

- Narrate the four unexpected capabilities (META_TOOLING.md).
- On-screen lower-thirds when each model fires: `SAM 3.1`, `Muse Wonder`, `Muse Image`, `Glimmer`.
- README table maps tool → module → demo timestamp.
- Avoid "we used Llama somewhere" filler. Depth > breadth theater — but we still use the full Muse family with real jobs.

### Demo (25%) — the actual contest

- Primary artifact is the **3-minute video**. Shoot as cinema, not a Loom dump.
- Live wow: **ghost pendulum locked to reality**.
- Backup: fixture replay indistinguishable from live if APIs flake.
- Cross-domain drop (cells) proves generality in 20 seconds.
- VERITAS beat = memorable closer / Meta-relevant integrity wink.

### Technical depth (20%) — show craft

- Held-out prediction gates (LLM proposes, maths decides).
- Sandboxed Toolsmith.
- Published eval table (even n≈8–20 clips).
- Cost router + prompt caching.
- Clean public repo, typed API, CI smoke tests.

## 2. Theme positioning

**Primary:** Push the Frontier  
**Secondary flavor:** Build for Your World (Indian classrooms Mitrazzz knows firsthand)

Submission form language (draft):

> HYPATIA gives machines a new capability: open-vocabulary active science on real video. It accelerates experiments by designing the next test via information gain, and produces verified laws that help understand physical systems — models meeting the real world through a webcam.

## 3. Campaign timeline (remaining window)

Today is **Sun Nov 1, 2026 (IST)**. Deadline **Wed Nov 4, 9:00 PM ET / Thu Nov 5, 7:30 AM IST**.

| Window (IST) | Focus | Win lever |
| --- | --- | --- |
| Nov 1 (today) | Skeleton + Observer/Measurer vertical slice | Technical depth start |
| Nov 2 | Hypothesis loop + first law E2E | Ambition |
| Nov 3 | Ghost imagination + Experiment UI + voice | Demo wow |
| Nov 4 daytime | Toolsmith/library OR VERITAS; evals; polish | Tooling story |
| Nov 4 evening | Feature freeze; shoot+edit video | Demo 25% |
| Nov 5 early AM IST | README, deploy verify, **submit** | Gate + Impact narrative |
| Nov 5–8 | Public clip push for viral bonus; Discord presence | Bonus $ |
| Nov 9 | Live finals rehearsal with fixtures | Stage Three |

See BUILD_PLAN.md for engineering milestones.

## 4. Demo campaign (beyond the form)

1. **Hero video** — YouTube + X/LinkedIn with tagline; pin in repo README.
2. **60s cutdown** — for social / Discord.
3. **Before/after** — Tracker manual clicking vs HYPATIA 90s Galileo.
4. **Build-in-public** — 3–5 posts: masks appear; first law; ghost lock; cells; submit.
5. **Most-viral bonus** — ask campus clubs / teacher communities to share the school-lab angle.

## 5. Live finals protocol (if top 5)

- Cold start from **Vercel → Modal** URL; warm Modal containers beforehand; local Docker failover.
- Script memorized; one person drives, one watches metrics.
- Pre-warm Meta `file_id`s; never upload raw 4K on stage.
- If judge asks "is the LLM just fitting?": answer with held-out gate + rival elimination + experiment design.

## 6. Team roles (≤4)

| Seat | Owns | Rubric |
| --- | --- | --- |
| Agent lead | Wonder PI, experiment designer, library | Tooling + Depth |
| Vision lead | SAM, calibration, Muse Image ghost/audit | Tooling + Demo |
| Science/evals | PySR, stats, test videos, VERITAS | Depth + Impact |
| Product/demo | UI, voice, video, README, socials | Demo + Impact |

Solo/duo: merge Agent+Science and Vision+Product.

## 7. Disqualification avoidance checklist

- [ ] Public repo
- [ ] Clear "Built during Oct 26 – Nov 4, 2026" section with commit range
- [ ] Rights to every video/asset listed in `data/videos/SOURCES.md`
- [ ] Demo only shows hackathon-built features (label any prior scaffolding honestly if any)
- [ ] Meta models actually called (include redacted request logs or cost dashboard screenshot)

## 8. Scorecard target (aspirational)

| Criterion | Weight | Target | Notes |
| --- | --- | --- | --- |
| Impact | 30% | 4/5 | Strong user story; not life-or-death like SURGE |
| Meta tooling | 25% | 5/5 | Six tools essential; four surprises |
| Demo | 25% | 5/5 | Ghost + three worlds |
| Technical depth | 20% | 4.5/5 | Gates + sandbox + evals |
| Theme gate | pass | 5/5 | Push the Frontier verbatim |

## 9. Kill criteria / pivot

If by **Tue Nov 3 night IST** we cannot show masks → trajectories → at least one held-out-accepted law on a pendulum clip, **narrow scope**: ship "Observer + Measurer + PySR law + geometric ghost" and keep Wonder as thin PI wrapper. Do **not** abandon Meta tool diversity — keep Image (notebook art) + Voice + Glimmer swarm even in thin mode.
