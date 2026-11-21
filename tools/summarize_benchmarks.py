#!/usr/bin/env python3
"""Summarize Sfumato vs Direct benchmark result files as a Markdown table.

Usage:
    python tools/summarize_benchmarks.py benchmarks/v2 [--strict] [--no-ablations]

Every ``*.json`` file in the directory is read, except files whose name starts
with ``_`` (briefs, scratch output). Each file holds one result object, or a
list of result objects, with this schema:

    {
      "problem_id": "MKT-DIS",
      "model": "gemini-4-neon-high",
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

Cross-model multi-run containers (an object with a ``"results"`` list whose
items carry benchmark fields, e.g. ``cross_model_claude.json``) are parsed too.
Their items may use the schema above or the flat schema ``direct_unique`` /
``direct_total`` / ``sfumato_unique`` / ``sfumato_total`` / ``blind_ab`` /
``blind_ba``; an item-level ``"model"`` overrides the container's. Other
containers (an ``"ablation"`` key, or a ``"results"`` list whose items carry no
benchmark fields) are skipped with a one-line note, not a warning.

Model labels are normalized (``gemini-4-neon-high`` and Antigravity "inherit"
runs -> ``gemini-4-neon``; ``claude-opus-5-5`` unchanged). When more than one
model is present, the table gains a ``Model`` column and per-model subtotal rows.

If ``<directory>/ablations/`` exists (and ``--no-ablations`` is not passed),
every ``v2_ablation_*.json`` in it is rendered as a second table, "v2.0 Stage 2b
Equal-Hardening Ablations": v1.2 baseline vs v2.0 hardened Sfumato:Direct judge
score sums, the Sfumato delta, and the verdict.

Per-problem outcome (from Sfumato's side): Win if Sfumato wins more judge
orders than Direct, Loss if fewer, otherwise Tie.

Exit codes: 0 = ok; 1 = no valid results, or invalid files under --strict;
2 = bad arguments.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ARMS = ("direct", "sfumato")
WINNERS = ("sfumato", "direct", "tie")
_RESULT_KEYS = ("direct", "sfumato", "blind_judges", "direct_unique", "sfumato_unique",
                "blind_ab", "blind_ba")
_EFFORT_SUFFIX = re.compile(r"-(?:low|medium|high|xhigh|max)$")
ABLATION_PREFIX = "v2_ablation_"


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


def normalize_model(label):
    """Map a free-form model label to a short canonical name ('-' if missing)."""
    if not isinstance(label, str) or not label.strip():
        return "-"
    low = label.strip().lower()
    m = re.search(r"claude-[a-z]+-[0-9]+(?:[-.][0-9]+)*", low)
    if m:
        return m.group(0)
    m = re.search(r"gemini-[0-9.]+(?:-[a-z]+)*", low)
    if m:
        return _EFFORT_SUFFIX.sub("", m.group(0))
    if "antigravity" in low:
        # Antigravity "inherit" runs used the CLI default model, Gemini 4 Neon.
        return "gemini-4-neon"
    return _EFFORT_SUFFIX.sub("", re.sub(r"\s+", "-", low))


def _is_container(obj):
    """True for multi-run files (cross-model, ablation) that are not single results."""
    return (isinstance(obj, dict) and "problem_id" not in obj
            and (isinstance(obj.get("results"), list) or "ablation" in obj))


def _looks_like_result(item):
    return (isinstance(item, dict) and "problem_id" in item
            and any(k in item for k in _RESULT_KEYS))


def _is_result_container(obj):
    """True for cross-model containers whose ``results`` items carry benchmark fields."""
    if not _is_container(obj) or "ablation" in obj:
        return False
    items = obj["results"]
    return bool(items) and all(_looks_like_result(i) for i in items)


def _unflatten(item):
    """Convert the flat cross-model item schema into the standard one."""
    if any(k in item for k in ("direct", "sfumato", "blind_judges")):
        return item
    out = dict(item)
    for arm in ARMS:
        if arm + "_unique" in item or arm + "_total" in item:
            out[arm] = {"unique": item.get(arm + "_unique"), "total": item.get(arm + "_total")}
    judges = {order.upper(): item["blind_" + order] for order in ("ab", "ba")
              if "blind_" + order in item}
    if judges:
        out["blind_judges"] = judges
    return out


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
        "model": normalize_model(obj.get("model")),
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


def _read_json(full):
    with open(full, "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


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
            data = _read_json(full)
        except (OSError, ValueError) as exc:
            errors.append((name, "unreadable JSON: %s" % exc))
            continue
        if _is_result_container(data):
            items = []
            for item in data["results"]:
                item = _unflatten(item)
                if "model" not in item and "model" in data:
                    item = dict(item, model=data["model"])
                items.append(item)
            labels = ["%s:results[%d]" % (name, i) for i in range(len(items))]
        elif _is_container(data):
            if skipped is not None:
                skipped.append(name)
            continue
        else:
            items = data if isinstance(data, list) else [data]
            labels = [name if len(items) == 1 else "%s[%d]" % (name, i)
                      for i in range(len(items))]
        for label, item in zip(labels, items):
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


def _outcome_counts(results):
    tally = {"Win": 0, "Tie": 0, "Loss": 0}
    for r in results:
        tally[outcome(r)] += 1
    return tally


def _sum_arms(results):
    tot = {a: {"unique": 0, "total": 0} for a in ARMS}
    for r in results:
        for a in ARMS:
            for k in ("unique", "total"):
                tot[a][k] += r[a][k]
    return tot


def render(results):
    """Return (markdown, tally) for a list of validated results."""
    models = sorted({r["model"] for r in results})
    multi = len(models) > 1

    def mcol(value):
        return " %s |" % value if multi else ""

    lines = [
        "| Problem |%s Direct Unique/Total | Sfumato Unique/Total | Diversity Multiplier "
        "| Judge AB | Judge BA | Outcome |" % mcol("Model"),
        "|---|%s---|---|---|---|---|---|" % ("---|" if multi else ""),
    ]
    tally = _outcome_counts(results)
    judge_tally = {w: 0 for w in WINNERS}
    for r in sorted(results, key=lambda r: (r["problem_id"], r["model"])):
        for j in r["blind_judges"].values():
            judge_tally[j["winner"]] += 1
        lines.append("| %s |%s %s | %s | %s | %s | %s | %s |" % (
            r["problem_id"], mcol(r["model"]), _ratio(r["direct"]), _ratio(r["sfumato"]),
            _multiplier(r["direct"], r["sfumato"]),
            _judge_cell(r["blind_judges"].get("AB")), _judge_cell(r["blind_judges"].get("BA")),
            outcome(r)))
    if multi:
        for m in models:
            sub = [r for r in results if r["model"] == m]
            st, sc = _sum_arms(sub), _outcome_counts(sub)
            lines.append("| *Subtotal (%d run%s)* | %s | %s | %s | %s | | | %dW / %dT / %dL |" % (
                len(sub), "" if len(sub) == 1 else "s", m, _ratio(st["direct"]),
                _ratio(st["sfumato"]), _multiplier(st["direct"], st["sfumato"]),
                sc["Win"], sc["Tie"], sc["Loss"]))
    tot = _sum_arms(results)
    lines.append("| **Total** |%s %s | %s | %s | | | |" % (
        " |" if multi else "", _ratio(tot["direct"]), _ratio(tot["sfumato"]),
        _multiplier(tot["direct"], tot["sfumato"])))
    lines.append("")
    scope = ("%d run(s) on %d model(s)" % (len(results), len(models)) if multi
             else "%d problem(s)" % len(results))
    lines.append(
        "**Overall (Sfumato vs Direct): %d Win / %d Tie / %d Loss** across %s; "
        "judge verdicts: %d sfumato / %d direct / %d tie." % (
            tally["Win"], tally["Tie"], tally["Loss"], scope,
            judge_tally["sfumato"], judge_tally["direct"], judge_tally["tie"]))
    return "\n".join(lines), tally


# --- Stage 2b equal-hardening ablations ----------------------------------------

def _winner_side(raw, where):
    w = str(raw or "").strip().lower()
    for side in WINNERS:
        if w.startswith(side):
            return side
    raise SchemaError("%s.winner must start with sfumato/direct/tie (got %r)" % (where, raw))


def _arm_score(judge, arm, where):
    for key in (arm + "_score", arm + "_hardened_score", arm + "_v2_hardened_score",
                arm + "_breakdown", arm + "_total", arm):
        if key in judge:
            return _score(judge[key], "%s.%s" % (where, key))
    raise SchemaError("%s has no %s score" % (where, arm))


def _judge_map(raw, where):
    if not isinstance(raw, dict) or not raw:
        raise SchemaError(where + " must be a non-empty object")
    for order, j in raw.items():
        if not isinstance(j, dict):
            raise SchemaError("%s.%s must be an object" % (where, order))
    return {str(k).upper(): v for k, v in raw.items()}


def _baseline_sums(base):
    """Return (sfumato_sum, direct_sum) for the v1.2 baseline."""
    if not isinstance(base, dict):
        raise SchemaError("baseline_v1_2 must be an object")
    if "total_sfumato" in base and "total_direct" in base:
        return (_num(base["total_sfumato"], "baseline_v1_2.total_sfumato"),
                _num(base["total_direct"], "baseline_v1_2.total_direct"))
    agg = base.get("aggregate")
    if isinstance(agg, dict) and "sfumato_sum" in agg and "direct_sum" in agg:
        return (_num(agg["sfumato_sum"], "baseline_v1_2.aggregate.sfumato_sum"),
                _num(agg["direct_sum"], "baseline_v1_2.aggregate.direct_sum"))
    judges = _judge_map(base.get("scores"), "baseline_v1_2.scores")
    return tuple(sum(_arm_score(j, arm, "baseline_v1_2.scores." + o) for o, j in judges.items())
                 for arm in ("sfumato", "direct"))


def validate_ablation(obj):
    """Return a normalized ablation row or raise SchemaError."""
    if not isinstance(obj, dict):
        raise SchemaError("ablation must be a JSON object")
    pid = obj.get("problem_id")
    if not isinstance(pid, str) or not pid.strip():
        raise SchemaError("problem_id must be a non-empty string")
    missing = [k for k in ("baseline_v1_2", "blind_judges") if k not in obj]
    if missing:
        raise SchemaError("missing required key(s): " + ", ".join(missing))
    base_s, base_d = _baseline_sums(obj["baseline_v1_2"])
    judges = _judge_map(obj["blind_judges"], "blind_judges")
    hard_s = sum(_arm_score(j, "sfumato", "blind_judges." + o) for o, j in judges.items())
    hard_d = sum(_arm_score(j, "direct", "blind_judges." + o) for o, j in judges.items())
    winners = [_winner_side(j.get("winner"), "blind_judges." + o) for o, j in judges.items()]
    return {"problem_id": pid.strip(), "model": normalize_model(obj.get("model")),
            "baseline": (base_s, base_d), "hardened": (hard_s, hard_d),
            "wins": winners.count("sfumato"), "losses": winners.count("direct")}


def load_ablations(path):
    """Return (rows, errors) for ``v2_ablation_*.json`` files in ``path``."""
    rows, errors = [], []
    for name in sorted(os.listdir(path)):
        low = name.lower()
        if not (low.startswith(ABLATION_PREFIX) and low.endswith(".json")):
            continue
        full = os.path.join(path, name)
        if not os.path.isfile(full):
            continue
        label = "ablations/" + name
        try:
            data = _read_json(full)
        except (OSError, ValueError) as exc:
            errors.append((label, "unreadable JSON: %s" % exc))
            continue
        try:
            rows.append(validate_ablation(data))
        except SchemaError as exc:
            errors.append((label, str(exc)))
    return rows, errors


def _signed(n):
    return ("+" if n > 0 else "") + _fmt(n)


def _ablation_verdict(row):
    w, l = row["wins"], row["losses"]
    if w > l:
        return "Sfumato %d-%d Win" % (w, l)
    if l > w:
        return "Direct %d-%d Win" % (l, w)
    return "Split %d-%d" % (w, l)


def render_ablations(rows):
    lines = [
        "### v2.0 Stage 2b Equal-Hardening Ablations",
        "",
        "| Problem | v1.2 Baseline (S:D) | v2.0 Hardened (S:D) | Sfumato Delta | Verdict |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(rows, key=lambda r: r["problem_id"]):
        (bs, bd), (hs, hd) = r["baseline"], r["hardened"]
        lines.append("| %s | %s:%s | %s:%s | %s | %s |" % (
            r["problem_id"], _fmt(bs), _fmt(bd), _fmt(hs), _fmt(hd), _signed(hs - bs),
            _ablation_verdict(r)))
    return "\n".join(lines)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Summarize Sfumato benchmark result JSON files.")
    ap.add_argument("directory", help="directory containing *.json result files")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any file fails validation")
    ap.add_argument("--no-ablations", action="store_true",
                    help="skip <directory>/ablations/v2_ablation_*.json")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.directory):
        print("error: not a directory: %s" % args.directory, file=sys.stderr)
        return 2
    skipped = []
    results, errors = load_dir(args.directory, skipped)
    ablations = []
    abl_dir = os.path.join(args.directory, "ablations")
    if not args.no_ablations and os.path.isdir(abl_dir):
        ablations, abl_errors = load_ablations(abl_dir)
        errors.extend(abl_errors)
    for name in skipped:
        print("note: skipped %s (container without benchmark results)" % name, file=sys.stderr)
    for name, msg in errors:
        print("warning: %s: %s" % (name, msg), file=sys.stderr)
    if not results:
        print("error: no valid result files in %s" % args.directory, file=sys.stderr)
        return 1
    table, _ = render(results)
    print(table)
    if ablations:
        print("")
        print(render_ablations(ablations))
    return 1 if (errors and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
