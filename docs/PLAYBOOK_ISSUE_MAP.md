# Active build sequence (project board)

Use **Playbook #** from the **[Build Playbook project](https://github.com/users/mitra9917/projects/4)** table (sort ascending). That row number is what Mitrazzz means by “playbook N” — it is **not** the same as GitHub issue #.

**Never use the script step index alone** — see `setup_github_project_playbook.py` table at bottom for automation-only mapping.

## Board rows 36–44 (canonical daily order)

| Playbook # | Issue | Title | Status |
| ---: | ---: | --- | --- |
| **36** | [**22**](https://github.com/mitra9917/HYPATIA/issues/22) | P2.4 Held-out scoring gate + bootstrap CIs | done (#92) |
| **37** | [**29**](https://github.com/mitra9917/HYPATIA/issues/29) | P3.4 Geometric ghost fallback renderer | done (#92) |
| **38** | [**58**](https://github.com/mitra9917/HYPATIA/issues/58) | P2.9 JSON schemas + API contract tests | done (#92) |
| **39** | [**30**](https://github.com/mitra9917/HYPATIA/issues/30) | P3.5 Experiment Designer (`/experiment/propose`) | done (#92) |
| **40** | [**23**](https://github.com/mitra9917/HYPATIA/issues/23) | P2.5 UI hypothesis cards + rival comparison | done (#92) |
| **41** | [**31**](https://github.com/mitra9917/HYPATIA/issues/31) | P3.6 HITL experiment UI + `/experiment/result` | done (#92) |
| **42** | [**57**](https://github.com/mitra9917/HYPATIA/issues/57) | P2.8 Accept law gates + POST `/accept` + UI commit | done (#92) |
| **43** | [**32**](https://github.com/mitra9917/HYPATIA/issues/32) | P3.7 Voice loop (`/api/voice/turn`) | done (#92) |
| **44** | [**59**](https://github.com/mitra9917/HYPATIA/issues/59) | P2.10 Observer narration in UI | done (#91) |

**Next up:** playbook **52+** after #50–#51 land.

## Board rows 45–49

| Playbook # | Issue | Title | Status |
| ---: | ---: | --- | --- |
| **45** | [**33**](https://github.com/mitra9917/HYPATIA/issues/33) | P3.8 Hybrid fixture/live ops switch | done (#93) |
| **46** | [**24**](https://github.com/mitra9917/HYPATIA/issues/24) | P2.6 Lab notebook markdown export | done (#93) |
| **47** | [**60**](https://github.com/mitra9917/HYPATIA/issues/60) | P3.9 Law library UI + chart | done (#93) |
| **48** | [**62**](https://github.com/mitra9917/HYPATIA/issues/62) | P3.11 Upload consent banner | done (#93) |
| **49** | [**61**](https://github.com/mitra9917/HYPATIA/issues/61) | P3.10 Voice WebSocket ASR | done (#93) |

## Board rows 50–51

| Playbook # | Issue | Title | Status |
| ---: | ---: | --- | --- |
| **50** | [**47**](https://github.com/mitra9917/HYPATIA/issues/47) | Modal Secrets + Volume + S3 prep | this PR |
| **51** | [**49**](https://github.com/mitra9917/HYPATIA/issues/49) | GitHub Actions secrets (CI deploy) | this PR |

---

# Full script mapping (`setup_github_project_playbook.py`)

Trust the **board table above** for daily work; use the table below only when reconciling automation.
| Script step | Issue |
| ---: | ---: |
| 1 | [44](https://github.com/mitra9917/HYPATIA/issues/44) |
| 2 | [2](https://github.com/mitra9917/HYPATIA/issues/2) |
| 3 | [3](https://github.com/mitra9917/HYPATIA/issues/3) |
| 4 | [5](https://github.com/mitra9917/HYPATIA/issues/5) |
| 5 | [48](https://github.com/mitra9917/HYPATIA/issues/48) |
| 6 | [4](https://github.com/mitra9917/HYPATIA/issues/4) |
| 7 | [45](https://github.com/mitra9917/HYPATIA/issues/45) |
| 8 | [46](https://github.com/mitra9917/HYPATIA/issues/46) |
| 9 | [6](https://github.com/mitra9917/HYPATIA/issues/6) |
| 10 | [7](https://github.com/mitra9917/HYPATIA/issues/7) |
| 11 | [8](https://github.com/mitra9917/HYPATIA/issues/8) |
| 12 | [9](https://github.com/mitra9917/HYPATIA/issues/9) |
| 13 | [10](https://github.com/mitra9917/HYPATIA/issues/10) |
| 14 | [11](https://github.com/mitra9917/HYPATIA/issues/11) |
| 15 | [50](https://github.com/mitra9917/HYPATIA/issues/50) |
| 16 | [56](https://github.com/mitra9917/HYPATIA/issues/56) |
| 17 | [12](https://github.com/mitra9917/HYPATIA/issues/12) |
| 18 | [13](https://github.com/mitra9917/HYPATIA/issues/13) |
| 19 | [51](https://github.com/mitra9917/HYPATIA/issues/51) |
| 20 | [14](https://github.com/mitra9917/HYPATIA/issues/14) |
| 21 | [55](https://github.com/mitra9917/HYPATIA/issues/55) |
| 22 | [15](https://github.com/mitra9917/HYPATIA/issues/15) |
| 23 | [18](https://github.com/mitra9917/HYPATIA/issues/18) |
| 24 | [52](https://github.com/mitra9917/HYPATIA/issues/52) |
| 25 | [16](https://github.com/mitra9917/HYPATIA/issues/16) |
| 26 | [53](https://github.com/mitra9917/HYPATIA/issues/53) |
| 27 | [54](https://github.com/mitra9917/HYPATIA/issues/54) |
| 28 | [17](https://github.com/mitra9917/HYPATIA/issues/17) |
| 29 | [19](https://github.com/mitra9917/HYPATIA/issues/19) |
| 30 | [20](https://github.com/mitra9917/HYPATIA/issues/20) |
| 31 | [21](https://github.com/mitra9917/HYPATIA/issues/21) |
| 32 | [22](https://github.com/mitra9917/HYPATIA/issues/22) |
| 33 | [58](https://github.com/mitra9917/HYPATIA/issues/58) |
| 34 | [23](https://github.com/mitra9917/HYPATIA/issues/23) |
| 35 | [57](https://github.com/mitra9917/HYPATIA/issues/57) |
| 36 | [59](https://github.com/mitra9917/HYPATIA/issues/59) |
| 37 | [24](https://github.com/mitra9917/HYPATIA/issues/24) |
| 38 | [25](https://github.com/mitra9917/HYPATIA/issues/25) |
| 39 | [26](https://github.com/mitra9917/HYPATIA/issues/26) |
| 40 | [27](https://github.com/mitra9917/HYPATIA/issues/27) |
| 41 | [28](https://github.com/mitra9917/HYPATIA/issues/28) |
| 42 | [29](https://github.com/mitra9917/HYPATIA/issues/29) |
| 43 | [30](https://github.com/mitra9917/HYPATIA/issues/30) |
| 44 | [31](https://github.com/mitra9917/HYPATIA/issues/31) |
| 45 | [32](https://github.com/mitra9917/HYPATIA/issues/32) |
| 46 | [33](https://github.com/mitra9917/HYPATIA/issues/33) |
| 47 | [60](https://github.com/mitra9917/HYPATIA/issues/60) |
| 48 | [62](https://github.com/mitra9917/HYPATIA/issues/62) |
| 49 | [61](https://github.com/mitra9917/HYPATIA/issues/61) |
| 50 | [47](https://github.com/mitra9917/HYPATIA/issues/47) |
| 51 | [49](https://github.com/mitra9917/HYPATIA/issues/49) |
| 52 | [34](https://github.com/mitra9917/HYPATIA/issues/34) |
| 53 | [35](https://github.com/mitra9917/HYPATIA/issues/35) |
| 54 | [36](https://github.com/mitra9917/HYPATIA/issues/36) |
| 55 | [37](https://github.com/mitra9917/HYPATIA/issues/37) |
| 56 | [64](https://github.com/mitra9917/HYPATIA/issues/64) |
| 57 | [39](https://github.com/mitra9917/HYPATIA/issues/39) |
| 58 | [66](https://github.com/mitra9917/HYPATIA/issues/66) |
| 59 | [63](https://github.com/mitra9917/HYPATIA/issues/63) |
| 60 | [40](https://github.com/mitra9917/HYPATIA/issues/40) |
| 61 | [67](https://github.com/mitra9917/HYPATIA/issues/67) |
| 62 | [65](https://github.com/mitra9917/HYPATIA/issues/65) |
| 63 | [41](https://github.com/mitra9917/HYPATIA/issues/41) |
| 64 | [42](https://github.com/mitra9917/HYPATIA/issues/42) |
| 65 | [43](https://github.com/mitra9917/HYPATIA/issues/43) |
| 66 | [38](https://github.com/mitra9917/HYPATIA/issues/38) |
| 67 | [68](https://github.com/mitra9917/HYPATIA/issues/68) |
