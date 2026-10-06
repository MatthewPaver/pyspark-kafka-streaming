# Audit fixes — 2026-09-05

Existing uncommitted schema/streaming template changes were preserved. No commit, push, deployment or Docker startup was performed; no remote service credentials were accessed.

## Changes

- Added `make integration`: a 240-second hard-bounded Compose/Kafka/Spark check. A unique topic receives one valid fixture and one malformed fixture; real Kafka source offsets pass through the shared parsing/classification functions into Parquet and JSON quarantine; exact records/lineage are asserted. Available-now queries terminate automatically and have their own 60-second limit. Normal cleanup removes only the fixture topic/temp files. CI runs the real target and stops its broker in an always step.
- Added a process-group deadline helper with tests for success, failure, hangs and a descendant that ignores SIGTERM after its parent exits. Independent review identified that last case; a failing heartbeat regression reproduced it before the helper was corrected to kill the remaining group.
- Fixed missing/null schema versions bypassing validation (`eqNullSafe` now rejects them); the reproduction first observed a malformed versionless event in the valid stream.
- Added a real finite file-source streaming test: duplicate events yield one window-metric count through the same metrics transform/output mode. This verifies local streaming execution without pretending it is Kafka integration.
- Set test shuffle partitions to two so a two-row check does not spend its deadline scheduling 400 empty state tasks. The initial finite-stream test hit its 30-second deadline at Spark's default 200 partitions; after the harness correction it completes.
- Exported repo-root PYTHONPATH with aligned driver/worker interpreters. `make check`/`make test` no longer reinstall dependencies. CI sets Java 17 explicitly.
- README distinguishes metrics deduplication from the replay-preserving valid-event log and states actual integration verification status.

## Verification

- `make test`: **8 passed in 10.54 seconds**, including real Spark contract/lineage, missing-version rejection, finite streaming duplicate metrics and process-tree deadline tests. No tests skipped.
- `make dataframe`: succeeded with Spark 3.5.8 / Java 17.0.6 and aligned Python 3.11; printed James Smith, Anna Rose and Robert Williams, then stopped Spark.
- `.venv/bin/python -m py_compile scripts/spark_kafka_integration.py scripts/run_bounded.py`: passed.
- `.venv/bin/python scripts/run_bounded.py --timeout 10 docker info --format '{{.ServerVersion}}'`: timed out, exit **124**, process group terminated. Docker daemon was not responding.
- **Real Kafka/connector target NOT RUN locally.** No connector download, topic, broker, output or checkpoint was created by that target. The added CI workflow has not been dispatched remotely.
- `git diff --check`: passed before final documentation updates.

## Remaining release gate

An owner needs a working Docker daemon and network/cache access to the pinned Kafka image and Spark connector, then runs `make integration` and retains the real result. This is a runnable candidate integration check, not a green integration result. It does not yet validate long-running late-data policy, restart recovery, throughput or production deployment.

Independent review by `prototype_design`; required process-tree cleanup issue was fixed with RED/GREEN evidence. No production support or blanket exactly-once guarantee is claimed.
