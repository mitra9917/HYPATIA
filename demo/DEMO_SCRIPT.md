# HYPATIA demo script (3:00)

Primary judging artifact. Record 1080p, landscape, one narrator. Live site: https://hypatia-chi.vercel.app

**One-line pitch:** HYPATIA is a camera that does science. It watches anything that moves, discovers the law, proves it by predicting the future, and tells you the next experiment to run.

**Hackathon fit:** Indie Developer track, **Push the Frontier** ("give a machine a new capability, accelerate a scientific experiment, and understand a physical system").

## Before you hit record

1. **Record the live-model parts locally.** The public site is locked to fixture mode so visitors cannot break it. That mode replays saved Meta outputs. Judges score "Use of Meta AI tooling", so show real calls for the Observer and Wonder beats.
   - Run the API locally in live mode (`FIXTURE_MODE=false`, `MODEL_API_KEY` set, ops mode `live` or `hybrid`).
   - Run one pendulum session and keep it open. The **PI plans · meta calls** panel at the bottom of the session page shows each model id, latency and token use. That panel is your proof.
   - Say honestly when you switch to the public site: "The live app replays recorded Meta outputs so it never stalls."
2. Open these tabs in order, zoomed to 125%: `/` (Home), `/lab`, a finished `/session/<id>`, `/settings`, `/library`, `/about`.
3. Pre-run one session so the session page is ready. Waiting on screen wastes your three minutes.
4. Hide `.env`, API keys, and AWS consoles. Never show the keys.
5. Only show what you built during the hackathon (Oct 26 to Nov 4). Do not show earlier projects.

## Script

| Time | Screen to show | What you say (spoken words) | Stack words on screen |
| --- | --- | --- | --- |
| 0:00 to 0:15 | **Home** (`/`). Hero text "The camera that does science." | "Every discovery in physics started with someone watching something move and asking why. HYPATIA is a camera that does that. It sees, measures, theorises, tests itself, and tells you what to do next." | Title card: *Indie Developer · Push the Frontier* |
| 0:15 to 0:30 | Stay on Home, scroll to the loop (observe, measure, hypothesize, imagine, audit, experiment, learn). | "This is not a chatbot that explains physics. It is a closed scientific loop. Seven stages, and every stage uses a Meta model. Muse Spark, Muse Wonder, Muse Image, Muse Voice Transcribe and SAM 3.1, all through the Meta Model API." | Lower third: *Meta Model API* |
| 0:30 to 1:00 | **Lab** (`/lab`). Tick the consent box, click **Run desk pendulum demo**. Watch the stepper fill. Then open the session. | "I point it at a desk pendulum. Muse Spark watches the video through the Responses API and returns a structured scene brief: what moves, what to measure. Then SAM 3.1 becomes the ruler. It masks the bob on every frame and I get angle against time in real units, with no hand tracking." | *Muse Spark · structured output* then *SAM 3.1* |
| 1:00 to 1:30 | **Session page**, **Observer · SAM tracking**, scrub the mask, then **Rival theories**. | "Now the key rule. The language model proposes, the maths decides. Rival theories compete: period proportional to length, to the square root of length, to mass. A swarm of open-weight Muse Glimmer candidates, wired through Modal, Baseten and Fireworks, feeds the contest. Held-out data and bootstrap checks pick the winner. No law gets accepted on a model's say-so." | *Muse Glimmer · open weights* then *Held-out scoring gate* |
| 1:30 to 1:55 | **Imagination audit** (ghost swinging), then the **Accept gate** card. | "Then it imagines the future. Muse Image draws where the pendulum will be, and SAM 3.1 audits that prediction against reality frame by frame. When the imagined swing matches the real one, the law is accepted. T equals two pi root L over g, and g comes out near nine point eight, with error bars. When Muse Image is imprecise it falls back to a geometric ghost, and SAM still checks it." | *Muse Image* then *SAM 3.1 audit* |
| 1:55 to 2:20 | **Next experiment · Muse Wonder** panel. Click the mic (**Voice**) and say "double the string length". Then show **PI plans · meta calls** (the local live recording). | "Muse Wonder is the principal investigator. It does not stop at a law. It picks the single most informative next experiment: double the string and watch the period rise by root two. I can answer by voice with Muse Voice Transcribe. This is an agent that plans, decides and coordinates, not a one-shot prompt." | *Muse Wonder · agentic planning* then *Muse Voice Transcribe* |
| 2:20 to 2:45 | **Settings** (`/settings`): Toolsmith, VERITAS, Biology.cells cards. Then **Law library** (`/library`). | "It also builds its own tools. Toolsmith writes and tests code in a sandbox, so a new domain like cell growth needs no new code from me. VERITAS runs the same physics check on suspicious clips: a falling ball at six metres per second squared is not real footage. Every accepted law lands in a library, so the next session starts smarter." | *Sandboxes · tool library* |
| 2:45 to 3:00 | **About** (`/about`), then end card with repo and live URL. | "A single model can describe the world. A system that measures it, tests itself against it and improves is something new. HYPATIA is the base layer for machines that run science. Built on Muse Spark, Wonder, Image, Voice Transcribe, SAM 3.1 and Glimmer. Thank you." | End card: GitHub URL, live URL, model list |

Spoken word count is about 430, which fits three minutes at a calm pace. If you run over, cut the Voice beat first, then the Toolsmith and VERITAS sentence.

## How to say "superintelligence" without overclaiming

Judges reward ambition but mark down claims the demo cannot back. Use this framing in the 2:45 beat or the end card:

- **Say:** "Narrow today, general by design. Today it discovers laws of motion and cell growth. The architecture is domain-agnostic: perception, measurement, theory, verification, experiment design, and a growing library of laws and tools."
- **Say:** "A system that perceives the world, forms hypotheses, tests them against reality, and chooses its next experiment is the loop every scientific discovery follows. HYPATIA closes that loop in software."
- **Do not say** it is already superintelligent, that it beats human scientists, or that it works on any video. Say what it did on screen.

## What is real vs scaffold (stay honest in Q&A)

| Claim | Status |
| --- | --- |
| Muse Spark observer, Wonder PI, SAM 3.1, Muse Image, Voice Transcribe via Meta Model API | Code paths exist and call live when `MODEL_API_KEY` is set and ops mode is live. Public site replays fixtures. |
| Muse Glimmer open-weight swarm | Adapter is wired for Modal, Baseten and Fireworks. The default returns a fixed rival list. Say "wired for", not "running on". |
| Muse Spark Open | Not used. Do not claim it. |
| Muse Code | Process claim only. Mention it only if you really built parts of HYPATIA with it. |
| Toolsmith sandbox | Runs a local subprocess today. Say "sandboxed tool testing". |

## Keyword checklist for the AI parser

The organisers list these terms on the event page. Say each one aloud once, and show it as text on screen:

- Meta Model API, Responses API, structured output
- Muse Spark series (Spark), Muse Wonder, Muse Image, Muse Voice Transcribe, SAM 3.1
- Meta open-weight models, Muse Glimmer
- Modal, Baseten, Fireworks (partner inference)
- Push the Frontier, Indie Developer track
- accelerate a scientific experiment, understand and control a physical system, give a machine a new capability (their wording)
- agentic, multi-step, autonomous (for the Best Agentic Use-Case prize)

## Rubric map

| Rubric item | Where this script earns it |
| --- | --- |
| Impact (30%) | Schools without lab kit, any phone as a lab (0:00 and 2:45) |
| Use of Meta AI tooling (25%) | Five Model API models plus open-weight Glimmer, each doing a distinct job (0:15 to 2:20) |
| Technical depth (20%) | Held-out gate, SAM audit of Muse Image, bootstrap error bars (1:00 to 1:55) |
| Demo (25%) | Working live site, one-click run (0:30) |

Bonus prizes you can reasonably go for: **Best Agentic Use-Case**, **Best Creative Build** (Muse Image and Wonder), **Best Build on Meta Open Weight Models** (only if Glimmer really runs on partner inference), and **Most Viral Project** (post the cut on X).

## Export and submission checklist

- [ ] 3:00 or less, burned-in captions, plus a separate `.srt`
- [ ] End card: GitHub URL, https://hypatia-chi.vercel.app, "Indie track · Push the Frontier"
- [ ] Upload unlisted to YouTube for judges, and a public cut for X
- [ ] X post: demo clip plus "Built with Muse Spark, Wonder, Image, Voice Transcribe, SAM 3.1 via the Meta Model API" and tag the hackathon
- [ ] Paste the live URL and video link into `docs/SUBMISSION_PACK.md` and the README
- [ ] Claim your $150 Meta Model API credits before **Wed Nov 4, 9:00 PM ET** (needs a card on the account)
