# HYPATIA — Indie submission pack (Playbook #62 / issue #65)

Use with [`README.md`](../README.md) and [`docs/HACKATHON_ALIGNMENT.md`](./HACKATHON_ALIGNMENT.md).

## One-line pitch

**HYPATIA is a camera that does science** — Meta models observe motion, SAM measures in SI units, maths accepts laws on held-out data, Muse Image predicts the future, Wonder designs the next experiment.

## Theme & track

| Field | Value |
| --- | --- |
| Event | Meta Global AI Developer Hackathon |
| Track | **Indie developer** |
| Theme | **Push the Frontier** |
| Secondary narrative | Build for Your World — Indian schools without lab equipment (`docs/PRODUCT.md`) |

## Links (fill before submit)

| Asset | URL |
| --- | --- |
| Public repo | https://github.com/mitra9917/HYPATIA |
| Live demo | _Modal ASGI + Vercel — see PRODUCTION_DEPLOY_CHECKLIST.md_ |
| Demo video (~3 min) | _YouTube/Loom — follow demo/DEMO_SCRIPT.md_ |

## Run from zero (judges)

```bash
git clone https://github.com/mitra9917/HYPATIA.git && cd HYPATIA
cp .env.example .env
./scripts/run_api_local.sh          # terminal 1
cd apps/web && npm ci && npm run dev  # terminal 2 → http://localhost:3000
./scripts/smoke_playbook_52_57.sh   # optional API smoke
```

Click **Run desk pendulum demo** (check ethics box for upload/webcam).

## Built during hackathon

Oct 26 – Nov 4, 2026 (ET). Public commit history on `main`; fixture mode enables review without Meta keys.

## Impact (30%)

Real user: student / maker with a phone camera. Real numbers: \(g\), period, VERITAS break frame, logistic growth export. Product path: law library + experiment designer.
