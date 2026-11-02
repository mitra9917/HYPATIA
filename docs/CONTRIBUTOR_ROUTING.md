# Spark Contributor routing (Playbook #27 / issue #54)

## Policy

| Role | Model env | Contributor allowed? |
| --- | --- | --- |
| Observer | `META_OBSERVER_MODEL` → `settings.observer_model` | Yes when `META_USE_CONTRIBUTOR=true` |
| PI | `META_PI_MODEL` (Wonder) | **Never** |
| Imagination | `META_IMAGE_MODEL` | **Never** |
| Measure / SAM | `META_SAM_MODEL` | **Never** |

`ModelRouter` validates Wonder/Image/SAM IDs at init and raises if a `-contributor` suffix appears.

## Enable

```bash
META_USE_CONTRIBUTOR=true
FIXTURE_MODE=false
MODEL_API_KEY=...
```

`/api/health` → `contributor_policy.observer_spark_tier` is `contributor` or `standard`.

## Logging

Each Spark Responses call logs (stdlib logger `hypatia.meta_client`):

```text
meta_spark_call model=muse-spark-1.3-contributor spark_routing=contributor kind=responses session_id=...
```

Session `meta_calls` entries include `spark_routing` on Spark models.

## UI

When Contributor mode is on, the lab shows a green **Spark Contributor mode** banner (policy reminder).
