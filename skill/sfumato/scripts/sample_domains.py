#!/usr/bin/env python3
"""Cluster-stratified random domain sampler for Sfumato.

Guarantees each sampled remote domain comes from a disjoint macro-cluster
so LLM brainstorming escapes its default cliché pool (ants, jazz, chess).
Pure Python stdlib, zero external dependencies.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

# Domains that may trigger false-positive bio/CBRN/cyber/defense refusals
# during Blind Isomorphic Masking on stricter safety filters (e.g. Claude).
CLAUDE_SAFE_EXCLUDE_IDS = {
    "immunology_microbiome",
    "parasitology_coevolution",
    "electronic_warfare_pls",
    "nuclear_passive_safety",
    "counter_intelligence",
    "submarine_acoustics",
    "arms_control_verification",
    "maritime_lazaretto",
}


def load_pool(pool_path: Path) -> dict[str, list[dict]]:
    data = json.loads(pool_path.read_text(encoding="utf-8"))
    return data["clusters"]


def sample_domains(
    clusters: dict[str, list[dict]],
    k: int,
    exclude_clusters: set[str],
    exclude_ids: set[str],
    seed: int | None,
) -> list[dict]:
    rng = random.Random(seed)
    eligible_clusters = [
        cname
        for cname, items in clusters.items()
        if cname not in exclude_clusters
        and any(item["id"] not in exclude_ids for item in items)
    ]
    if not eligible_clusters:
        raise ValueError("No eligible clusters left after exclusions.")

    rng.shuffle(eligible_clusters)
    picked: list[dict] = []
    used_ids = set(exclude_ids)

    # Round-robin across shuffled clusters to maximize cluster disjointness
    while len(picked) < k:
        progressed = False
        for cname in eligible_clusters:
            if len(picked) >= k:
                break
            candidates = [i for i in clusters[cname] if i["id"] not in used_ids]
            if not candidates:
                continue
            choice = rng.choice(candidates)
            used_ids.add(choice["id"])
            picked.append({"cluster": cname, **choice})
            progressed = True
        if not progressed:
            break
        rng.shuffle(eligible_clusters)

    return picked


def assign_tracks(items: list[dict], mode: str) -> list[dict]:
    out = []
    for idx, item in enumerate(items):
        if mode == "explicit-only":
            track = "explicit"
        elif mode == "blind-only":
            track = "blind"
        else:
            track = "explicit" if idx % 2 == 0 else "blind"
        out.append({"track": track, **item})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Sample disjoint remote domains.")
    parser.add_argument("--k", type=int, default=4, help="Number of domains to sample (default: 4)")
    parser.add_argument(
        "--mode",
        choices=["dual-track", "explicit-only", "blind-only"],
        default="dual-track",
        help="Track assignment mode (default: dual-track)",
    )
    parser.add_argument(
        "--exclude-clusters",
        type=str,
        default="",
        help="Comma-separated macro-cluster names to exclude (e.g. markets_law,craft_operations)",
    )
    parser.add_argument(
        "--exclude-ids",
        type=str,
        default="",
        help="Comma-separated domain IDs to exclude",
    )
    parser.add_argument(
        "--safe-profile",
        choices=["full", "claude"],
        default="full",
        help="Filter out bio/CBRN/cyber/espionage domains that may trigger false-positive refusals on Claude (default: full)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Optional RNG seed for reproducibility")
    parser.add_argument("--list-clusters", action="store_true", help="List available macro-clusters and exit")
    args = parser.parse_args()

    pool_path = Path(__file__).resolve().parent.parent / "resources" / "domain_pool.json"
    clusters = load_pool(pool_path)

    if args.list_clusters:
        for cname, items in clusters.items():
            print(f"{cname} ({len(items)}): {', '.join(i['id'] for i in items)}")
        return 0

    exclude_clusters = {c.strip() for c in args.exclude_clusters.split(",") if c.strip()}
    exclude_ids = {i.strip() for i in args.exclude_ids.split(",") if i.strip()}
    if args.safe_profile == "claude":
        exclude_ids |= CLAUDE_SAFE_EXCLUDE_IDS

    sampled = sample_domains(clusters, args.k, exclude_clusters, exclude_ids, args.seed)
    assigned = assign_tracks(sampled, args.mode)

    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(assigned, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
