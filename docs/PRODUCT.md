# HYPATIA — Product Spec

## One-line pitch

**HYPATIA turns any camera into a self-driving science lab.** It watches anything move, discovers the law behind it, proves the law by predicting the future, and tells you the one experiment that will test it best. It gets smarter with every video.

## Tagline (video / X / submission)

> We gave Meta's models a camera and the scientific method. It rediscovered Galileo on my desk in 90 seconds.

## Problem

Science = look → guess a rule → test → repeat. Today humans do every step by hand:

- Click objects frame-by-frame (Tracker, cell annotation tools)
- Dump numbers into spreadsheets
- Try formulas until one fits
- Decide the next experiment from intuition

That fails at scale:

| Who | Pain | Evidence we cite |
| --- | --- | --- |
| Indian secondary schools | No integrated science lab | ~1.25 lakh schools without labs (UDISE+ 2024–25) |
| Biology / materials researchers | Hours of video, tiny gold-standard labels | Cell Tracking Challenge: expert labels cover ~17.8% of cells |
| Science as a system | Irreproducible, slow | >70% researchers failed to reproduce others' work (Nature 2016); self-driving labs cut experiments ~6× |

## Solution — the closed scientific loop

HYPATIA automates the full loop on **any** camera or video file:

1. **Observe** — understand the scene (what moves, what variables matter)
2. **Measure** — pixels → physical quantities (metres, radians, seconds) via SAM 3.1 + calibration
3. **Hypothesise** — rival theories proposed in parallel (swarm + symbolic regression)
4. **Imagine** — predict future frames; Muse Image draws the predicted world
5. **Audit** — SAM measures the imagined frame vs the real next frame
6. **Experiment** — pick the highest expected-information-gain next test; ask human (or drive a simulator via computer use)
7. **Learn** — keep surviving laws + tools; next similar scene is faster/cheaper

## Exact user-facing capabilities (v1 for hackathon)

### Core (must ship)

| Capability | User sees |
| --- | --- |
| Webcam / upload science session | Start live webcam or drop an MP4/MOV |
| Live object masks + trajectories | SAM overlays; angle/length/position time series |
| Rival hypothesis cards | 2–5 competing laws with scores |
| Next experiment recommendation | Plain English: "Double the string length. If period ×1.41, Theory B wins." |
| Ghost prediction overlay | Translucent predicted motion over real video; live error meter |
| Lab notebook export | Law, constants ± error bars, code, video clip, measurement CSV |
| Voice control | "What if I use a heavier bob?" via Muse Voice Transcribe |

### Domain demos (same engine, zero new product code)

| World | Input | Outcome |
| --- | --- | --- |
| Pendulum / free fall / ramp | Desk webcam | Recover \(T = 2\pi\sqrt{L/g}\) or \(s = \tfrac12 at^2\); measure \(g\) |
| Cell / colony growth | Public microscopy time-lapse | Logistic growth + doubling time; Toolsmith writes cell-count tool if missing |
| AI-generated physics video | Viral / generated clip | VERITAS module: "acceleration ≠ 9.8; frame N breaks momentum — not real" |

### Stretch (ship if time)

- Computer-use path: change PhET / browser simulator parameters autonomously
- Glimmer local swarm: hundreds of candidate equations offline
- Self-improvement chart: time-to-law across sessions (library hit rate)

## Non-goals (v1)

- Custom hardware / robots / sensors beyond webcam and phone video
- Training foundation models from scratch
- Replacing professional lab instruments for regulated metrology
- Surveillance / crowd monitoring as the primary product (SURGE is backup narrative only)

## Personas

1. **Student / teacher** — phone + desk experiment; needs explanation + next step
2. **Research assistant** — batch of time-lapse videos; needs laws + notebook
3. **Integrity / fact-check** — viral clip; needs physics verdict with frame evidence
4. **World-model researcher** (aspirational) — wants verified law-labeled video

## Product path (Impact 30%)

1. Free web app for NCERT-style practicals (India-first story)
2. Video lab notebook for research labs
3. API: videos → checked physical laws (training signal for world models)

## Success metrics for the hackathon demo

| Metric | Target |
| --- | --- |
| End-to-end pendulum law recovery | Correct form; \(g\) within ±10% of 9.8 |
| Ghost overlay sync | Visually locked for ≥8–10 seconds; pixel error visibly low |
| Cross-domain transfer | Same agent handles ≥2 worlds without new code |
| Meta tool essentiality | Removing any of Spark / Wonder / Image / SAM / Glimmer visibly breaks a demo beat |
| Demo runtime | ≤3:00 polished video; live backup ≤4 minutes |

## Novelty claim we defend

Academic video→equation systems exist (VER, VIPER-R1, IRIS, MAGE…). HYPATIA's novelty is the **closed active loop**:

1. Active experiment design on real video (not passive fitting)
2. Open-vocabulary measurement (SAM as scientific instrument)
3. Imagination audited by measurement (Muse Image as falsifiable prediction)
4. Self-tooling + memory (Wonder Toolsmith + law/tool library)
5. One engine, many worlds, no new human code

## Competitive contrast (one slide)

| System | Passive fit | Active experiment | Real video | Self-tools | Visual prediction audit |
| --- | --- | --- | --- | --- | --- |
| Tracker | human | no | yes | no | no |
| VER / VIPER-R1 | yes | no | yes | no | no |
| SciExplorer | yes | yes | simulated only | limited | no |
| Self-driving labs | yes | yes | instrument-specific | hardware | no |
| **HYPATIA** | **yes** | **yes** | **yes** | **yes** | **yes** |
