#!/usr/bin/env python3
"""Cluster-stratified random domain sampler for Sfumato.

Guarantees each sampled remote domain comes from a disjoint macro-cluster
so LLM brainstorming escapes its default cliché pool (ants, jazz, chess).
Pure Python stdlib, zero external dependencies.
"""

from __future__ import annotations

import argparse
import json
import math
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


POLARITIES = ("adversarial", "cooperative", "physical_loop", "human_ux", "systems_ops")


def load_pool(pool_path: Path) -> dict[str, list[dict]]:
    data = json.loads(pool_path.read_text(encoding="utf-8"))
    return data["clusters"]


def sample_domains(
    clusters: dict[str, list[dict]],
    k: int,
    exclude_clusters: set[str],
    exclude_ids: set[str],
    seed: int | None,
    polarity: str = "any",
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

    if polarity and polarity != "any":
        # Soft polarity weighting: the first ceil(k/2) picks come from disjoint clusters
        # that hold an affinity-matching domain (choosing among matching domains there);
        # the rest come from the other disjoint clusters. Falls back gracefully when too
        # few matching clusters remain, then continues with the round-robin below.
        def matches(item: dict) -> bool:
            return item["id"] not in used_ids and polarity in item.get("affinities", [])

        need = math.ceil(k / 2)
        matching = [c for c in eligible_clusters if any(matches(i) for i in clusters[c])]
        first_round = matching[:need]
        rest = [c for c in eligible_clusters if c not in first_round]
        for cname in first_round:
            choice = rng.choice([i for i in clusters[cname] if matches(i)])
            used_ids.add(choice["id"])
            picked.append({"cluster": cname, **choice})
        for cname in rest:
            if len(picked) >= k:
                break
            choice = rng.choice([i for i in clusters[cname] if i["id"] not in used_ids])
            used_ids.add(choice["id"])
            picked.append({"cluster": cname, **choice})
        if len(picked) >= k:
            return picked[:k]
        rng.shuffle(eligible_clusters)

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


def all_domains(
    clusters: dict[str, list[dict]],
    exclude_clusters: set[str],
    exclude_ids: set[str],
    seed: int | None,
) -> list[list[dict]]:
    """Return every eligible domain, grouped per cluster (shuffled cluster and item order)."""
    rng = random.Random(seed)
    groups: list[list[dict]] = []
    for cname, items in clusters.items():
        if cname in exclude_clusters:
            continue
        kept = [{"cluster": cname, **i} for i in items if i["id"] not in exclude_ids]
        if kept:
            rng.shuffle(kept)
            groups.append(kept)
    if not groups:
        raise ValueError("No eligible clusters left after exclusions.")
    rng.shuffle(groups)
    return groups


def strip_hints(items: list[dict], include_hints: bool) -> list[dict]:
    """Drop ``mechanisms`` (hint priming) unless explicitly requested."""
    if include_hints:
        return items
    return [{k: v for k, v in item.items() if k != "mechanisms"} for item in items]


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


def main(argv: list[str] | None = None) -> int:
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
    parser.add_argument(
        "--polarity",
        choices=("any",) + POLARITIES,
        default="any",
        help="Soft-weight sampling so at least ceil(k/2) domains share this structural affinity (default: any)",
    )
    parser.add_argument(
        "--include-hints",
        action="store_true",
        help="Include each domain's 'mechanisms' hints in the output (omitted by default to avoid hint priming)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Optional RNG seed for reproducibility")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Return ALL eligible domains grouped by cluster (ignores --k)",
    )
    parser.add_argument("--list-clusters", action="store_true", help="List available macro-clusters and exit")
    args = parser.parse_args(argv)

    pool_path = Path(__file__).resolve().parent.parent / "resources" / "domain_pool.json"
    clusters = load_pool(pool_path)

    if args.list_clusters:
        for cname, items in clusters.items():
            print(f"{cname} ({len(items)}): {', '.join(i['id'] for i in items)}")
        return 0

    if args.k < 1:
        parser.error(f"--k must be >= 1 (got {args.k})")

    exclude_clusters = {c.strip() for c in args.exclude_clusters.split(",") if c.strip()}
    exclude_ids = {i.strip() for i in args.exclude_ids.split(",") if i.strip()}
    unknown_clusters = sorted(exclude_clusters - set(clusters))
    if unknown_clusters:
        parser.error(
            f"unknown --exclude-clusters: {', '.join(unknown_clusters)}. "
            f"Valid clusters: {', '.join(clusters)}"
        )
    valid_ids = [i["id"] for items in clusters.values() for i in items]
    unknown_ids = sorted(exclude_ids - set(valid_ids))
    if unknown_ids:
        parser.error(
            f"unknown --exclude-ids: {', '.join(unknown_ids)}. "
            f"Valid ids: {', '.join(valid_ids)}"
        )
    if args.safe_profile == "claude":
        exclude_ids |= CLAUDE_SAFE_EXCLUDE_IDS

    if args.all:
        # Tracks alternate explicit/blind within each cluster (or follow --mode).
        try:
            groups = all_domains(clusters, exclude_clusters, exclude_ids, args.seed)
        except ValueError as exc:
            parser.error(str(exc))
        assigned = [item for group in groups for item in assign_tracks(group, args.mode)]
    else:
        try:
            sampled = sample_domains(
                clusters, args.k, exclude_clusters, exclude_ids, args.seed, args.polarity
            )
        except ValueError as exc:
            parser.error(str(exc))
        assigned = assign_tracks(sampled, args.mode)
    assigned = strip_hints(assigned, args.include_hints)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(assigned, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
