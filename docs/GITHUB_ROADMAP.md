# GitHub roadmap (issues mirror)

## Build playbook (use this daily)

**[HYPATIA Build Playbook — Project #4](https://github.com/users/mitra9917/projects/4)** (public)

| View | How |
| --- | --- |
| **Table** | Sort by **Playbook #** ascending → work top to bottom |
| **Board** | Group by **Status**: **Up next** → **In progress** → **Done** |

**Workflow:** Only one issue in **In progress**. Finish it → move to **Done** → pull the next **Up next** card (lowest Playbook #).

**Step 1 (you):** [#2 Meta API key](https://github.com/mitra9917/HYPATIA/issues/2) — then [#3 Modal](https://github.com/mitra9917/HYPATIA/issues/3), etc.

If any issue is missing from the board, run:

```bash
python3 scripts/setup_github_project_playbook.py
```

Meta checklist (parallel): **[Issue #44](https://github.com/mitra9917/HYPATIA/issues/44)**.

## Milestones

| Milestone | Outcome |
| --- | --- |
| [M0](https://github.com/mitra9917/HYPATIA/milestone/1) | Integrations you configure (keys, Modal, Vercel, partners) |
| [M1](https://github.com/mitra9917/HYPATIA/milestone/2) | Perception: Spark → SAM → trajectories + frontend shell |
| [M2](https://github.com/mitra9917/HYPATIA/milestone/3) | First law: Glimmer + Wonder + PySR + accept gate |
| [M3](https://github.com/mitra9917/HYPATIA/milestone/4) | Ghost, experiment, voice, library UI |
| [M4](https://github.com/mitra9917/HYPATIA/milestone/5) | Deploy, CI, evals, video, submit |

## Meta stack → issues

| Tool | Issues |
| --- | --- |
| Muse Spark 1.3 | #11–13, #54, #58 |
| Spark Contributor | #54, #2 |
| Muse Wonder | #21, #30, #34, #38, #68 |
| Muse Image | #27 |
| SAM 3.1 | #13, #28, #51 |
| Muse Glimmer | #4, #20, #45–46 |
| Muse Voice | #32, #59 |
| Muse Code | #7 |
| Muse Spark Open | #8 |
| Responses + Files API | #11, #50, #57 |
| meta_sam_parser / @meta-sam/parser | #51 |
| Computer use | #38, #68 |

## Closed loop (business logic)

1. Create session (#15, #50, #53)  
2. Observe (#12, #58)  
3. Measure (#13–14, #51)  
4. Hypothesize (#20–22, #21)  
5. Imagine + audit (#26–28)  
6. Experiment (#30–31)  
7. Accept law (#57, #24)  

Orchestration: **#56**. Frontend visibility: **#52**. Failure modes: **#63**, `docs/RISKS.md`.
