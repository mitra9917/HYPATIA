# Evaluation Plan

Evals are how we convert "cool demo" into **Technical Depth (20%)** and proof for Impact.

## 1. Datasets

| Set | Contents | Rights |
| --- | --- | --- |
| `desk-mechanics` | Pendulum, free fall, ramp, spring, cooling drop — our recordings | Own |
| `bio-public` | 1–2 public microscopy time-lapses | Cite licenses in `data/videos/SOURCES.md` |
| `synthetic-fake` | AI-generated physics violations | Own generations or clearly licensed |
| `iris-style` (optional) | Simple known dynamics clips | As licensed |

Target: **≥8 clips** for README table; stretch 20.

## 2. Metrics

### Law recovery

- Exact form match (symbolic, up to algebraically equivalent rewrite)
- Parameter error (e.g. \(|g-9.806|/9.806\)) — report % within 5% and 10%
- Time-to-law (seconds wall clock, excluding human experiment wait)

### Active vs passive

- Number of interventions to identify true law
- Compare Experiment Designer vs random / fixed schedule

### Imagination audit

- Mean SAM centroid error (px and metres) for physics-guided Muse Image vs naive prompt vs geometric renderer

### Self-improvement

- Session 1 vs session N: time, token $, SAM frames, library hit rate

### VERITAS

- Accuracy real vs AI-generated on small labeled set
- Frame-level localization: predicted break frame within ±k of human mark

## 3. Harness

```bash
python -m evals.run --suite desk-mechanics --mode fixture|live
```

Outputs:

- `evals/results/YYYYMMDD_summary.md`
- `evals/results/YYYYMMDD.json`

CI runs **fixture** mode only.

## 4. README presentation (judges scan this)

| Clip | True law | Recovered | \(g\) or key const | Active expts | Ghost MAE |
| --- | --- | --- | --- | --- | --- |
| pendulum_01 | \(T=2\pi\sqrt{L/g}\) | … | … | 1 | … |
| … | | | | | |

Plus one chart image: time-to-law vs session.

## 5. Honesty rules

- Never cherry-pick without reporting failures.
- Mark fixture vs live rows.
- If a law fails the held-out gate, show the rejection — that *is* the product.
