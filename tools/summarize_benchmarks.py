#!/usr/bin/env python3
"""Summarize Sfumato vs Direct benchmark result files as a Markdown table.

Usage:
    python tools/summarize_benchmarks.py benchmarks/v1_1_weekend/ [--strict]

Every ``*.json`` file in the directory is read, except files whose name starts
with ``_`` (briefs, scratch output). Each file holds one result object, or a
list of result objects, with this schema:

    {
      "problem_id": "MKT-DIS",
      "direct":  {"unique": 6,  "total": 24},
      "sfumato": {"unique": 18, "total": 24},
      "blind_judges": {
        "AB": {"winner": "sfumato", "scores": {"sfumato": 24, "direct": 21}},
        "BA": {"winner": "sfumato", "scores": {"sfumato": 23, "direct": 20}}
      }
    }

Accepted aliases: ``unique_mechanisms`` / ``total_ideas`` for ``unique`` /
``total``; flat ``sfumato_score`` / ``direct_score`` inside a judge object for
``scores``. Order keys are case-insensitive ("ab" == "AB"). Extra keys are
ignored. ``blind_judges`` may also be a list of objects carrying an ``"order"`` key
("AB" / "BA"). ``winner`` is one of ``sfumato``, ``direct`` or ``tie``;
``scores`` is optional. Each score may be a plain number or an object with a
numeric ``total`` (e.g. ``{"novelty": 9, "effectiveness": 5, "total": 18}``).

Container files that are not single-problem results (an object with a
``"results"`` list or an ``"ablation"`` key and no ``problem_id``, such as
cross-model runs) are skipped with a one-line note, not a warning.

Per-problem outcome (from Sfumato's side): Win if Sfumato wins more judge
orders than Direct, Loss if fewer, otherwise Tie.

Exit codes: 0 = ok; 1 = no valid results, or invalid files under --strict;
2 = bad arguments.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ARMS = ("direct", "sfumato")
WINNERS = ("sfumato", "direct", "tie")


class SchemaError(ValueError):
    pass


def _int(value, where):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SchemaError("%s must be a non-negative integer (got %r)" % (where, value))
    return value


def _num(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SchemaError("%s must be a number (got %r)" % (where, value))
    return value


def _score(value, where):
    if isinstance(value, dict):
        if "total" not in value:
            raise SchemaError("%s must be a number or an object with 'total' (got %r)" % (where, value))
        return _num(value["total"], where + ".total")
    return _num(value, where)


def _is_container(obj):
    """True for multi-run files (cross-model, ablation) that are not single results."""
    return (isinstance(obj, dict) and "problem_id" not in obj
            and (isinstance(obj.get("results"), list) or "ablation" in obj))


def _arm(obj, name):
    arm = obj.get(name)
    if not isinstance(arm, dict):
        raise SchemaError("'%s' must be an object with 'unique' and 'total'" % name)
    u_key = "unique" if "unique" in arm else "unique_mechanisms"
    t_key = "total" if "total" in arm else "total_ideas"
    unique = _int(arm.get(u_key), "%s.%s" % (name, u_key))
    total = _int(arm.get(t_key), "%s.%s" % (name, t_key))
    if unique > total:
        raise SchemaError("%s.unique (%d) exceeds %s.total (%d)" % (name, unique, name, total))
    return {"unique": unique, "total": total}


def _judge(j, order):
    where = "blind_judges." + order
    if not isinstance(j, dict):
        raise SchemaError(where + " must be an object")
    winner = j.get("winner")
    if not isinstance(winner, str) or winner.lower() not in WINNERS:
        raise SchemaError("%s.winner must be one of %s (got %r)" % (where, "/".join(WINNERS), winner))
    scores = j.get("scores")
    if scores is None:
        flat = {k: j[k + "_score"] for k in ARMS if k + "_score" in j}
        scores = flat or None
    if scores is not None:
        if not isinstance(scores, dict):
            raise SchemaError(where + ".scores must be an object")
        scores = {k: _score(scores[k], "%s.scores.%s" % (where, k)) for k in ARMS if k in scores}
    return {"winner": winner.lower(), "scores": scores or {}}


def validate(obj):
    """Return a normalized result dict or raise SchemaError."""
    if not isinstance(obj, dict):
        raise SchemaError("result must be a JSON object")
    missing = [k for k in ("problem_id",) + ARMS + ("blind_judges",) if k not in obj]
    if missing:
        raise SchemaError("missing required key(s): " + ", ".join(missing))
    pid = obj["problem_id"]
    if not isinstance(pid, str) or not pid.strip():
        raise SchemaError("problem_id must be a non-empty string")

    raw = obj["blind_judges"]
    if isinstance(raw, list):
        judges_in = {}
        for i, j in enumerate(raw):
            if not isinstance(j, dict) or not isinstance(j.get("order"), str):
                raise SchemaError("blind_judges[%d] needs an 'order' key" % i)
            judges_in[j["order"].upper()] = j
    elif isinstance(raw, dict):
        judges_in = {str(k).upper(): v for k, v in raw.items()}
    else:
        raise SchemaError("blind_judges must be an object or a list")
    if not judges_in:
        raise SchemaError("blind_judges is empty")
    judges = {order: _judge(j, order) for order, j in judges_in.items()}

    return {
        "problem_id": pid.strip(),
        "direct": _arm(obj, "direct"),
        "sfumato": _arm(obj, "sfumato"),
        "blind_judges": judges,
    }


def outcome(result):
    verdicts = [j["winner"] for j in result["blind_judges"].values()]
    wins, losses = verdicts.count("sfumato"), verdicts.count("direct")
    if wins > losses:
        return "Win"
    if wins < losses:
        return "Loss"
    return "Tie"


def load_dir(path, skipped=None):
    """Return (results, errors) for all result files in ``path``.

    Names of skipped container files are appended to ``skipped`` if given.
    """
    results, errors = [], []
    for name in sorted(os.listdir(path)):
        if not name.lower().endswith(".json") or name.startswith("_"):
            continue
        full = os.path.join(path, name)
        if not os.path.isfile(full):
            continue
        try:
            with open(full, "r", encoding="utf-8-sig") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            errors.append((name, "unreadable JSON: %s" % exc))
            continue
        if _is_container(data):
            if skipped is not None:
                skipped.append(name)
            continue
        items = data if isinstance(data, list) else [data]
        for i, item in enumerate(items):
            label = name if len(items) == 1 else "%s[%d]" % (name, i)
            try:
                results.append(validate(item))
            except SchemaError as exc:
                errors.append((label, str(exc)))
    return results, errors


def _ratio(arm):
    return "%d / %d" % (arm["unique"], arm["total"])


def _multiplier(direct, sfumato):
    d, s = direct["unique"], sfumato["unique"]
    if d == 0:
        return "n/a" if s == 0 else "inf"
    return "%.2fx" % (s / d)


def _fmt(n):
    return str(int(n)) if float(n).is_integer() else "%g" % n


def _judge_cell(judge):
    if judge is None:
        return "-"
    sc = judge["scores"]
    if "sfumato" in sc and "direct" in sc:
        return "%s (S %s : D %s)" % (judge["winner"], _fmt(sc["sfumato"]), _fmt(sc["direct"]))
    return judge["winner"]


def render(results):
    """Return (markdown, tally) for a list of validated results."""
    lines = [
        "| Problem | Direct Unique/Total | Sfumato Unique/Total | Diversity Multiplier "
        "| Judge AB | Judge BA | Outcome |",
        "|---|---|---|---|---|---|---|",
    ]
    tally = {"Win": 0, "Tie": 0, "Loss": 0}
    judge_tally = {w: 0 for w in WINNERS}
    tot = {a: {"unique": 0, "total": 0} for a in ARMS}
    for r in sorted(results, key=lambda r: r["problem_id"]):
        o = outcome(r)
        tally[o] += 1
        for j in r["blind_judges"].values():
            judge_tally[j["winner"]] += 1
        for a in ARMS:
            for k in ("unique", "total"):
                tot[a][k] += r[a][k]
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["problem_id"], _ratio(r["direct"]), _ratio(r["sfumato"]),
            _multiplier(r["direct"], r["sfumato"]),
            _judge_cell(r["blind_judges"].get("AB")), _judge_cell(r["blind_judges"].get("BA")), o))
    lines.append("| **Total** | %s | %s | %s | | | |" % (
        _ratio(tot["direct"]), _ratio(tot["sfumato"]), _multiplier(tot["direct"], tot["sfumato"])))
    lines.append("")
    lines.append(
        "**Overall (Sfumato vs Direct): %d Win / %d Tie / %d Loss** across %d problem(s); "
        "judge verdicts: %d sfumato / %d direct / %d tie." % (
            tally["Win"], tally["Tie"], tally["Loss"], len(results),
            judge_tally["sfumato"], judge_tally["direct"], judge_tally["tie"]))
    return "\n".join(lines), tally


def main(argv=None):
    ap = argparse.ArgumentParser(description="Summarize Sfumato benchmark result JSON files.")
    ap.add_argument("directory", help="directory containing *.json result files")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any file fails validation")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.directory):
        print("error: not a directory: %s" % args.directory, file=sys.stderr)
        return 2
    skipped = []
    results, errors = load_dir(args.directory, skipped)
    for name in skipped:
        print("note: skipped %s (multi-run container, not a single-problem result)" % name,
              file=sys.stderr)
    for name, msg in errors:
        print("warning: %s: %s" % (name, msg), file=sys.stderr)
    if not results:
        print("error: no valid result files in %s" % args.directory, file=sys.stderr)
        return 1
    table, _ = render(results)
    print(table)
    return 1 if (errors and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
