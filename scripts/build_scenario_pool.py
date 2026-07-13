"""Build the pre-validated scenario pool.

Generates candidate scenarios across seeds and target difficulties, runs each
through the full validation gauntlet, and keeps only those that pass. The output
is a balanced pool (roughly equal Easy / Normal / Hard by MEASURED difficulty)
written to JSON.

Every entry records the generation id ("gen-<seed>-<target>") so the exact board
can be rebuilt deterministically, plus the difficulty the validator actually
measured (which is what the player is shown) and headline baseline metrics.

Usage:
    python -m scripts.build_scenario_pool [per_bucket] [max_seed]

    per_bucket : how many validated scenarios to keep per measured difficulty
                 (default 20)
    max_seed   : highest seed to scan before giving up (default 600)

Later (Phase 5/DB), load scenario_pool.json into the Supabase `scenarios` table.
The app selects a scenario the user hasn't played yet and rebuilds it with
build_scenario(entry["id"]).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from sim.data.scenarios import DIFFICULTIES, generate_scenario, seed_to_scenario_id
from sim.data.scenario_validator import validate_scenario


POOL_PATH = Path(__file__).resolve().parent.parent / "sim" / "data" / "scenario_pool.json"


def build_pool(per_bucket: int = 20, max_seed: int = 600) -> dict:
    buckets: dict[str, list[dict]] = {"Easy": [], "Normal": [], "Hard": []}
    scanned = 0
    rejected = 0

    for seed in range(1, max_seed + 1):
        if all(len(v) >= per_bucket for v in buckets.values()):
            break
        for target in DIFFICULTIES:
            scanned += 1
            rep = validate_scenario(generate_scenario(seed, target))
            if not rep.ok:
                rejected += 1
                continue
            bucket = buckets.get(rep.difficulty)
            if bucket is None or len(bucket) >= per_bucket:
                continue
            bucket.append({
                "id": seed_to_scenario_id(seed, target),
                "seed": seed,
                "target_difficulty": target,
                "difficulty": rep.difficulty,
                "avg_bsc": rep.avg_bsc,
                "final_stock": rep.final_stock,
                "cumulative_profit": rep.cumulative_profit,
            })

    scenarios = [s for bucket in buckets.values() for s in bucket]
    return {
        "scenarios": scenarios,
        "summary": {
            "total": len(scenarios),
            "by_difficulty": {k: len(v) for k, v in buckets.items()},
            "candidates_scanned": scanned,
            "rejected": rejected,
        },
    }


def main() -> None:
    per_bucket = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    max_seed = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    print(f"Building scenario pool: {per_bucket} per difficulty, scanning seeds 1..{max_seed}")
    pool = build_pool(per_bucket, max_seed)
    POOL_PATH.write_text(json.dumps(pool, indent=2), encoding="utf-8")
    s = pool["summary"]
    print(f"\nWrote {s['total']} scenarios to {POOL_PATH}")
    print(f"  by difficulty: {s['by_difficulty']}")
    print(f"  scanned {s['candidates_scanned']} candidates, rejected {s['rejected']}")


if __name__ == "__main__":
    main()
