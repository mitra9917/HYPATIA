# Risks & Fallbacks

| Risk | Likelihood | Impact | Fallback |
| --- | --- | --- | --- |
| Muse Image cannot place objects precisely | Med | Demo wow dies | **API auto-fallback:** `_imagine` sets `source=geometric` when Muse Image fails or returns empty; mask-hinted edits; SAM still audits |
| SAM 3.1 slow / limited from India | Med | Pipeline stalls | Cache tracks; open SAM on Modal; fixture mode |
| LLM invents plausible but wrong laws | High | Trust / depth | Held-out prediction gate; always show rivals; bootstrap CIs |
| Motion blur / bad lighting | Med | Bad tracks | 60fps phone, bright light, high-contrast bob; backup clips |
| Muse Wonder cost blows $150 credits | Med | Can't iterate | Wonder for plan only; Spark Contributor for volume; Glimmer swarm |
| Near-identical academic project appears | Low–Med | Novelty attack | Lead with imagination audit + self-tooling + active loop |
| Modal/Vercel cold start during judging | Med | Slow first click | `min_containers=1` on Modal API/Glimmer Nov 4–9; fixture fallback; video is primary artifact |
| Modal GPU credits exhausted | Med | No Glimmer | Spark substitute swarm; Baseten/Fireworks failover; honest README note |
| Partner GPU (Glimmer) not ready | Med | Open-weights story weak | CPU stub swarm with Spark drafts; document intent + partial run |
| Computer-use flaky on PhET | High | Stretch fails | Cut from demo; keep HITL experiment ask |
| Team bandwidth (≤4 / solo) | High | Scope creep | Kill order: computer-use → fine-tune → cells → VERITAS → voice → ghost → first law |
| Rights / ethics on crowd or student video | Low | DQ | Only owned / licensed clips; SOURCES.md |
| Unclear "new work during hackathon" | Med | DQ | Public commits dated in window; README Built-During section |

## Kill order (if behind)

1. Cut computer-use  
2. Cut Glimmer fine-tune (keep offline swarm or Spark substitute)  
3. Cut live cells (use one recorded success)  
4. Cut VERITAS beat (keep as README footnote)  
5. Cut voice  
6. **Never cut:** SAM measurement, held-out law gate, ghost (geometric OK), experiment recommendation, public deploy, 3-min video  

## Incident runbook (live demo)

1. Flip UI to `hybrid`  
2. If still failing → `fixture` with verbal: "replaying a recorded scientific session with the same agent trace"  
3. Continue script; do not debug Meta status on camera  
