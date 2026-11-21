#!/usr/bin/env python3
"""Tests for tools/summarize_benchmarks.py and the installers (stdlib only).

Run: python tools/test_tools.py
Installer tests never touch the real home directory: they pass an explicit
temporary home (-HomeDir / --home). Tests are skipped when the shell is absent.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import summarize_benchmarks as sb  # noqa: E402


def _result(pid, d_u, d_t, s_u, s_t, ab, ba, ab_scores=(24, 21), ba_scores=(23, 20)):
    return {
        "problem_id": pid,
        "direct": {"unique": d_u, "total": d_t},
        "sfumato": {"unique": s_u, "total": s_t},
        "blind_judges": {
            "AB": {"winner": ab, "scores": {"sfumato": ab_scores[0], "direct": ab_scores[1]}},
            "BA": {"winner": ba, "scores": {"sfumato": ba_scores[0], "direct": ba_scores[1]}},
        },
    }


class SummarizeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sfm-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, obj, raw=None):
        with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as fh:
            fh.write(raw if raw is not None else json.dumps(obj))

    def _run(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sb.main([self.tmp] + list(extra))
        return code, out.getvalue(), err.getvalue()

    def test_non_ascii_stdout_utf8_subprocess(self):
        self._write("tr.json", _result("İSTANBUL-1", 2, 4, 3, 4, "sfumato", "sfumato"))
        self._write("ru.json", _result("Şükrü-Model", 1, 4, 1, 4, "tie", "tie"))
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.pop("PYTHONUTF8", None)
        p = subprocess.run([sys.executable, "-B", os.path.join(HERE, "summarize_benchmarks.py"),
                            self.tmp, "--strict"], capture_output=True, env=env, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", "replace"))
        out = p.stdout.decode("utf-8")
        self.assertIn("İSTANBUL-1", out)
        self.assertIn("Şükrü-Model", out)
        self.assertEqual(p.stderr.decode("utf-8"), "")

    def test_table_and_tally(self):
        self._write("mkt.json", _result("MKT-DIS", 6, 24, 18, 24, "sfumato", "sfumato"))
        self._write("oss.json", _result("OSS-PR", 5, 12, 5, 12, "direct", "sfumato"))
        self._write("eng.json", _result("ENG-X", 4, 12, 3, 12, "direct", "direct",
                                        ab_scores=(19.5, 22), ba_scores=(20, 21)))
        self._write("_brief.json", None, raw="")          # underscore files ignored
        self._write("notes.txt", None, raw="not json")    # non-json ignored
        code, out, err = self._run("--strict")
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")
        self.assertIn("| MKT-DIS | 6 / 24 | 18 / 24 | 3.00x | sfumato (S 24 : D 21) "
                      "| sfumato (S 23 : D 20) | Win |", out)
        self.assertIn("| OSS-PR | 5 / 12 | 5 / 12 | 1.00x |", out)
        self.assertIn("direct (S 19.5 : D 22)", out)
        self.assertIn("| **Total** | 15 / 48 | 26 / 48 | 1.73x |", out)
        self.assertIn("1 Win / 1 Tie / 1 Loss** across 3 problem(s)", out)
        self.assertIn("judge verdicts: 3 sfumato / 3 direct / 0 tie", out)
        # rows sorted by problem id
        self.assertLess(out.index("ENG-X"), out.index("MKT-DIS"))
        self.assertLess(out.index("MKT-DIS"), out.index("OSS-PR"))

    def test_list_judges_and_multi_result_file(self):
        r1 = _result("A", 0, 4, 2, 4, "tie", "tie")
        r2 = _result("B", 0, 4, 0, 4, "sfumato", "tie")
        r2["blind_judges"] = [
            {"order": "ab", "winner": "Sfumato"},
            {"order": "BA", "winner": "tie", "scores": {"sfumato": 3, "direct": 3}},
        ]
        self._write("multi.json", [r1, r2])
        code, out, err = self._run()
        self.assertEqual(code, 0, err)
        self.assertIn("| A | 0 / 4 | 2 / 4 | inf |", out)
        self.assertIn("| B | 0 / 4 | 0 / 4 | n/a | sfumato | tie (S 3 : D 3) | Win |", out)
        self.assertIn("1 Win / 1 Tie / 0 Loss", out)

    def test_alias_schema(self):
        rich = {
            "problem_id": "MKT-DIS", "title": "t", "model": "m",
            "direct": {"runs": 4, "total_ideas": 8, "unique_mechanisms": 3, "unique_list": ["a"]},
            "sfumato": {"runs": 4, "total_ideas": 8, "unique_mechanisms": 7},
            "blind_judges": {
                "ab": {"a_is": "direct", "b_is": "sfumato", "direct_score": 21,
                       "sfumato_score": 24, "winner": "sfumato", "reason": "r"},
                "ba": {"a_is": "sfumato", "b_is": "direct", "direct_score": 20,
                       "sfumato_score": 23, "winner": "sfumato", "reason": "r"},
            },
            "outcome": "sfumato_win_2_0",
        }
        self._write("mkt_dis_results.json", rich)
        code, out, err = self._run("--strict")
        self.assertEqual(code, 0, err)
        self.assertIn("| MKT-DIS | 3 / 8 | 7 / 8 | 2.33x | sfumato (S 24 : D 21) "
                      "| sfumato (S 23 : D 20) | Win |", out)

    def test_schema_errors(self):
        bad_cases = [
            ({"direct": {}, "sfumato": {}, "blind_judges": {}}, "problem_id"),
            ({**_result("X", 1, 2, 1, 2, "tie", "tie"), "direct": {"unique": 3, "total": 2}}, "exceeds"),
            ({**_result("X", 1, 2, 1, 2, "tie", "tie"), "sfumato": {"unique": -1, "total": 2}}, "non-negative"),
            ({**_result("X", 1, 2, 1, 2, "tie", "tie"), "blind_judges": {}}, "empty"),
            ({**_result("X", 1, 2, 1, 2, "tie", "tie"), "blind_judges": {"AB": {"winner": "both"}}}, "winner"),
            ({**_result("X", 1, 2, 1, 2, "tie", "tie"), "blind_judges": [{"winner": "tie"}]}, "order"),
            ([1, 2], "JSON object"),
        ]
        for obj, needle in bad_cases:
            with self.subTest(needle=needle):
                with self.assertRaises(sb.SchemaError) as ctx:
                    sb.validate(obj)
                self.assertIn(needle, str(ctx.exception))

    def test_invalid_file_warns_and_strict_fails(self):
        self._write("good.json", _result("G", 1, 2, 2, 2, "sfumato", "sfumato"))
        self._write("broken.json", None, raw="{not json")
        self._write("missing.json", {"problem_id": "M"})
        code, out, err = self._run()
        self.assertEqual(code, 0)
        self.assertIn("warning: broken.json", err)
        self.assertIn("warning: missing.json: missing required key(s): direct, sfumato, blind_judges", err)
        self.assertIn("| G |", out)
        code, _, _ = self._run("--strict")
        self.assertEqual(code, 1)

    def test_empty_dir_and_bad_dir(self):
        code, _, err = self._run()
        self.assertEqual(code, 1)
        self.assertIn("no valid result files", err)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(sb.main([os.path.join(self.tmp, "nope")]), 2)

    def test_nested_total_score_dicts(self):
        r = _result("WEB-SCR", 2, 8, 5, 8, "sfumato", "direct")
        r["blind_judges"]["AB"]["scores"] = {
            "sfumato": {"novelty": 9, "effectiveness": 7, "feasibility": 6, "total": 22},
            "direct": {"novelty": 9, "effectiveness": 5, "feasibility": 4, "total": 18}}
        r["blind_judges"]["BA"] = {
            "winner": "direct",
            "sfumato_score": {"novelty": 7, "effectiveness": 7, "feasibility": 6.5, "total": 20.5},
            "direct_score": 21}
        self._write("web.json", r)
        code, out, err = self._run("--strict")
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")
        self.assertIn("sfumato (S 22 : D 18)", out)
        self.assertIn("direct (S 20.5 : D 21)", out)
        # a dict without a numeric total is still a schema error
        r["blind_judges"]["AB"]["scores"]["direct"] = {"novelty": 9}
        with self.assertRaises(sb.SchemaError):
            sb.validate(r)
        r["blind_judges"]["AB"]["scores"]["direct"] = {"total": "18"}
        with self.assertRaises(sb.SchemaError):
            sb.validate(r)

    def test_container_files_skipped_without_warning(self):
        self._write("mkt.json", _result("MKT-DIS", 3, 8, 7, 8, "sfumato", "sfumato"))
        self._write("xmodel.json", {"model": "m", "results": [{"problem_id": "MKT-DIS"}],
                                    "summary": {}})
        self._write("abl.json", {"ablation": {"k": [1, 2]}})
        code, out, err = self._run("--strict")
        self.assertEqual(code, 0, err)
        self.assertNotIn("warning", err)
        self.assertIn("note: skipped abl.json", err)
        self.assertIn("note: skipped xmodel.json", err)
        self.assertIn("across 1 problem(s)", out)

    def test_cross_model_flat_container_parsed(self):
        self._write("mkt.json", dict(_result("MKT-DIS", 3, 8, 7, 8, "sfumato", "sfumato"),
                                     model="gemini-4-neon-high"))
        self._write("xmodel.json", {"model": "claude-opus-5-5", "results": [{
            "problem_id": "MKT-DIS", "direct_unique": 4, "direct_total": 8,
            "sfumato_unique": 7, "sfumato_total": 8,
            "blind_ab": {"direct_score": 19, "sfumato_score": 18, "winner": "direct"},
            "blind_ba": {"direct_score": 17, "sfumato_score": 20, "winner": "sfumato"}}]})
        code, out, err = self._run("--strict")
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")
        self.assertIn("| Problem | Model |", out)
        self.assertIn("| MKT-DIS | claude-opus-5-5 | 4 / 8 | 7 / 8 | 1.75x | direct (S 18 : D 19) "
                      "| sfumato (S 20 : D 17) | Tie |", out)
        self.assertIn("| MKT-DIS | gemini-4-neon | 3 / 8 | 7 / 8 |", out)
        self.assertIn("| **Total** | | 7 / 16 | 14 / 16 | 2.00x |", out)
        self.assertIn("across 2 run(s) on 2 model(s)", out)
        self.assertIn("| *Subtotal (1 run)* | claude-opus-5-5 | 4 / 8 | 7 / 8 | 1.75x | | | 0W / 1T / 0L |", out)

    def test_cross_model_container_bad_item_warns(self):
        self._write("xmodel.json", {"model": "m", "results": [
            {"problem_id": "A", "direct_unique": 9, "direct_total": 8, "sfumato_unique": 1,
             "sfumato_total": 8, "blind_ab": {"winner": "tie"}},
            dict(_result("B", 1, 2, 2, 2, "sfumato", "sfumato"))]})
        code, out, err = self._run()
        self.assertEqual(code, 0)
        self.assertIn("warning: xmodel.json:results[0]: direct.unique (9) exceeds", err)
        self.assertIn("| B |", out)
        self.assertEqual(self._run("--strict")[0], 1)

    def test_normalize_model(self):
        cases = {"gemini-4-neon-high": "gemini-4-neon", "antigravity-inherit": "gemini-4-neon",
                 "Antigravity (Model=inherit)": "gemini-4-neon",
                 "antigravity-self (inherit)": "gemini-4-neon",
                 "claude-opus-5-5": "claude-opus-5-5", None: "-", "": "-", "My Model": "my-model"}
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(sb.normalize_model(raw), want)

    def test_ablations_table_and_errors(self):
        self._write("mkt.json", _result("MKT-DIS", 3, 8, 7, 8, "sfumato", "sfumato"))
        os.makedirs(os.path.join(self.tmp, "ablations"))
        abl = {"problem_id": "X-1",
               "baseline_v1_2": {"scores": {"ab": {"direct": 24, "sfumato": 22, "winner": "direct"},
                                            "ba": {"direct": 23, "sfumato": 21, "winner": "direct"}}},
               "blind_judges": {
                   "ab": {"direct_score": 22, "sfumato_score": {"total": 25}, "winner": "sfumato_v2_hardened"},
                   "ba": {"direct_hardened_score": {"total": 20}, "sfumato_v2_hardened_score": {"total": 23},
                          "winner": "sfumato_v2_hardened"}}}
        with open(os.path.join(self.tmp, "ablations", "v2_ablation_x.json"), "w") as f:
            json.dump(abl, f)
        with open(os.path.join(self.tmp, "ablations", "other_results.json"), "w") as f:
            f.write("{not json")  # not v2_ablation_* -> ignored
        code, out, err = self._run("--strict")
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")
        self.assertIn("### v2.0 Stage 2b Equal-Hardening Ablations", out)
        self.assertIn("| X-1 | 43:47 | 48:42 | +5 | Sfumato 2-0 Win |", out)
        code, out, _ = self._run("--strict", "--no-ablations")
        self.assertEqual(code, 0)
        self.assertNotIn("Ablations", out)
        with open(os.path.join(self.tmp, "ablations", "v2_ablation_bad.json"), "w") as f:
            json.dump({"problem_id": "BAD", "baseline_v1_2": {"total_direct": 1}}, f)
        code, out, err = self._run()
        self.assertEqual(code, 0)
        self.assertIn("warning: ablations/v2_ablation_bad.json: missing required key(s): blind_judges", err)
        self.assertEqual(self._run("--strict")[0], 1)


class RealBenchmarksTests(unittest.TestCase):
    """Smoke test: benchmarks/v2 is the single source of truth for the README table."""

    def test_v2_strict(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sb.main([BENCH_V2, "--strict"])
        out, err = out.getvalue(), err.getvalue()
        self.assertEqual(code, 0, err)
        self.assertNotIn("warning", err)
        rows = [l for l in out.splitlines()
                if l.startswith("| ") and ("| gemini-4-neon |" in l or "| claude-opus-5-5 |" in l)
                and not l.startswith("| *Subtotal")]
        self.assertEqual(len(rows), 9, "\n".join(rows))
        self.assertEqual(sum("| claude-opus-5-5 |" in l for l in rows), 2)
        self.assertEqual(sum("| MKT-DIS |" in l for l in rows), 2)
        self.assertIn("| **Total** | | 34 / 72 | 60 / 72 | 1.76x |", out)
        self.assertIn("across 9 run(s) on 2 model(s)", out)
        self.assertIn("### v2.0 Stage 2b Equal-Hardening Ablations", out)
        self.assertIn("| DOC-ROT | 43:48 | 46:48 | +3 | Split 1-1 |", out)
        self.assertIn("| GAME-SNOWBALL | 43:46 | 39:45 | -4 | Direct 2-0 Win |", out)


def _tree(path):
    found = []
    for root, _dirs, files in os.walk(path):
        for f in files:
            found.append(os.path.relpath(os.path.join(root, f), path).replace(os.sep, "/"))
        for d in _dirs:
            found.append(os.path.relpath(os.path.join(root, d), path).replace(os.sep, "/") + "/")
    return sorted(found)


POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


def _find_bash():
    """Prefer Git Bash on Windows; System32/bash.exe is WSL and cannot read C:/ paths."""
    if os.name == "nt":
        for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432"),
                     os.environ.get("ProgramFiles(x86)"), os.environ.get("LOCALAPPDATA")):
            if not base:
                continue
            for rel in (("Git", "bin", "bash.exe"), ("Programs", "Git", "bin", "bash.exe")):
                cand = os.path.join(base, *rel)
                if os.path.isfile(cand):
                    return cand
        git = shutil.which("git")
        if git:
            cand = os.path.join(os.path.dirname(os.path.dirname(git)), "bin", "bash.exe")
            if os.path.isfile(cand):
                return cand
    return shutil.which("bash")


BASH = _find_bash()
BASH_IS_WSL = bool(BASH) and os.name == "nt" and os.path.normcase(
    os.path.dirname(BASH)).endswith(os.path.normcase(os.path.join("windows", "system32")))


SAMPLER = os.path.join(REPO, "skill", "sfumato", "scripts", "sample_domains.py")


POOL_PATH = os.path.join(REPO, "skill", "sfumato", "resources", "domain_pool.json")
BENCH_V2 = os.path.join(REPO, "benchmarks", "v2")


def _load_script(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sd = _load_script(SAMPLER, "sample_domains")
with open(POOL_PATH, encoding="utf-8") as _fh:
    POOL = json.load(_fh)["clusters"]
ALL_IDS = {i["id"] for items in POOL.values() for i in items}
AFFINITY = {i["id"]: set(i.get("affinities", [])) for items in POOL.values() for i in items}


def _claude_count(items):
    return sum(1 for i in items if i["id"] not in sd.CLAUDE_SAFE_EXCLUDE_IDS)


class SampleDomainsTests(unittest.TestCase):
    def _proc(self, *args):
        return subprocess.run([sys.executable, "-B", SAMPLER] + list(args), capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=60)

    def _run(self, *args):
        p = self._proc(*args)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return json.loads(p.stdout)

    def _call(self, *args):
        """In-process run (fast, for many-seed loops)."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(sd.main(list(args)), 0)
        return json.loads(out.getvalue())

    def _assert_grouped(self, items):
        seen = []
        for it in items:
            if not seen or seen[-1] != it["cluster"]:
                self.assertNotIn(it["cluster"], seen, "clusters must be contiguous")
                seen.append(it["cluster"])
        return seen

    def test_all_full_profile(self):
        items = self._run("--all", "--safe-profile", "full", "--seed", "7", "--k", "2")
        self.assertEqual(len(items), len(ALL_IDS))
        self.assertEqual({i["id"] for i in items}, ALL_IDS)
        self.assertEqual(len(self._assert_grouped(items)), len(POOL))

    def test_all_claude_profile_per_cluster_counts_and_alternating_tracks(self):
        items = self._run("--all", "--safe-profile", "claude", "--seed", "3")
        self.assertEqual(len(items), len(ALL_IDS - sd.CLAUDE_SAFE_EXCLUDE_IDS))
        clusters = self._assert_grouped(items)
        self.assertEqual(len(clusters), sum(1 for v in POOL.values() if _claude_count(v)))
        for c in clusters:
            group = [i for i in items if i["cluster"] == c]
            self.assertEqual(len(group), _claude_count(POOL[c]), c)
            expected = ["explicit" if n % 2 == 0 else "blind" for n in range(len(group))]
            self.assertEqual([i["track"] for i in group], expected, c)
        self.assertEqual(items, self._run("--all", "--safe-profile", "claude", "--seed", "3"))

    def test_all_respects_mode_and_exclusions(self):
        items = self._run("--all", "--mode", "blind-only", "--safe-profile", "claude")
        self.assertTrue(all(i["track"] == "blind" for i in items))
        first = items[0]
        last = items[-1]
        self.assertNotEqual(first["cluster"], last["cluster"])
        items2 = self._run("--all", "--exclude-clusters", first["cluster"],
                           "--exclude-ids", last["id"], "--safe-profile", "claude")
        self.assertEqual(len(items2), len(items) - _claude_count(POOL[first["cluster"]]) - 1)
        self.assertNotIn(first["cluster"], {i["cluster"] for i in items2})
        self.assertNotIn(last["id"], {i["id"] for i in items2})

    def test_k_default_unchanged(self):
        items = self._run("--seed", "1")
        self.assertEqual(len(items), 4)
        self.assertEqual(len({i["cluster"] for i in items}), 4)
        self.assertEqual([i["track"] for i in items], ["explicit", "blind"] * 2)
        self.assertEqual(len(self._run("--k", "6", "--seed", "1")), 6)

    def test_clusters_disjoint_up_to_pool_size(self):
        for k in range(1, len(POOL) + 1):
            for seed in range(5):
                for pol in ("any",) + sd.POLARITIES:
                    items = self._call("--k", str(k), "--seed", str(seed), "--polarity", pol)
                    with self.subTest(k=k, seed=seed, polarity=pol):
                        self.assertEqual(len(items), k)
                        self.assertEqual(len({i["cluster"] for i in items}), k)
                        self.assertEqual(len({i["id"] for i in items}), k)

    def test_k_above_cluster_count_still_unique_ids(self):
        items = self._call("--k", str(len(POOL) + 3), "--seed", "2", "--polarity", "human_ux")
        self.assertEqual(len(items), len(POOL) + 3)
        self.assertEqual(len({i["id"] for i in items}), len(items))

    def test_claude_safe_profile_never_returns_excluded_ids(self):
        for seed in range(50):
            for pol in ("any", "adversarial", "physical_loop"):
                items = self._call("--k", "6", "--seed", str(seed), "--safe-profile", "claude",
                                   "--polarity", pol)
                with self.subTest(seed=seed, polarity=pol):
                    self.assertFalse({i["id"] for i in items} & sd.CLAUDE_SAFE_EXCLUDE_IDS)

    def test_polarity_soft_weighting(self):
        for pol in ("physical_loop", "human_ux", "adversarial"):
            for k in (2, 3, 4, 5):
                need = -(-k // 2)
                for seed in range(30):
                    for profile in ("full", "claude"):
                        items = self._call("--k", str(k), "--seed", str(seed), "--polarity", pol,
                                           "--safe-profile", profile)
                        with self.subTest(polarity=pol, k=k, seed=seed, profile=profile):
                            hits = sum(1 for i in items if pol in AFFINITY[i["id"]])
                            self.assertGreaterEqual(hits, need)
                            self.assertEqual(len({i["cluster"] for i in items}), k)
                            for i in items:
                                self.assertEqual(set(i["affinities"]), AFFINITY[i["id"]])

    def test_polarity_falls_back_when_few_matching_clusters(self):
        # Exclude every cluster that has a human_ux domain except one; still returns k picks.
        ux = [c for c, items in POOL.items() if any("human_ux" in i["affinities"] for i in items)]
        excluded = ux[1:]
        k = len(POOL) - len(excluded)
        items = self._call("--k", str(k), "--seed", "4", "--polarity", "human_ux",
                           "--exclude-clusters", ",".join(excluded))
        self.assertEqual(len(items), k)
        self.assertGreaterEqual(sum(1 for i in items if "human_ux" in AFFINITY[i["id"]]), 1)
        self.assertFalse({i["cluster"] for i in items} & set(excluded))

    def test_polarity_cli_acceptance(self):
        items = self._run("--k", "4", "--polarity", "physical_loop", "--safe-profile", "claude",
                          "--seed", "42")
        self.assertEqual(len(items), 4)
        self.assertGreaterEqual(sum(1 for i in items if "physical_loop" in AFFINITY[i["id"]]), 2)
        self.assertFalse({i["id"] for i in items} & sd.CLAUDE_SAFE_EXCLUDE_IDS)
        self.assertTrue(all("mechanisms" not in i for i in items))

    def test_include_hints(self):
        for extra in ((), ("--all",)):
            items = self._run("--seed", "5", *extra)
            self.assertTrue(items)
            self.assertTrue(all("mechanisms" not in i for i in items), extra)
            self.assertTrue(all("affinities" in i for i in items), extra)
            hinted = self._run("--seed", "5", "--include-hints", *extra)
            self.assertTrue(all(isinstance(i.get("mechanisms"), (list, str)) and i["mechanisms"]
                                for i in hinted), extra)
            self.assertEqual([i["id"] for i in items], [i["id"] for i in hinted])

    def test_seed_determinism(self):
        for pol in ("any", "cooperative"):
            a = self._run("--k", "5", "--seed", "123", "--polarity", pol)
            self.assertEqual(a, self._run("--k", "5", "--seed", "123", "--polarity", pol))
        runs = {json.dumps(self._call("--k", "4", "--seed", str(s))) for s in range(10)}
        self.assertGreater(len(runs), 1)

    def test_invalid_k_rejected(self):
        for k in ("0", "-1"):
            p = self._proc("--k", k)
            self.assertEqual(p.returncode, 2, k)
            self.assertIn("--k must be >= 1", p.stderr)
            self.assertEqual(p.stdout, "")

    def test_unknown_exclusions_rejected(self):
        p = self._proc("--exclude-clusters", "markets_law,not_a_cluster")
        self.assertEqual(p.returncode, 2)
        self.assertIn("not_a_cluster", p.stderr)
        self.assertIn("Valid clusters:", p.stderr)
        self.assertIn("markets_law", p.stderr)
        p = self._proc("--exclude-ids", "typo_domain")
        self.assertEqual(p.returncode, 2)
        self.assertIn("typo_domain", p.stderr)
        self.assertIn("Valid ids:", p.stderr)
        p = self._proc("--polarity", "chaotic")
        self.assertEqual(p.returncode, 2)

    def test_excluding_everything_is_a_clean_error(self):
        p = self._proc("--exclude-clusters", ",".join(POOL))
        self.assertEqual(p.returncode, 2)
        self.assertIn("No eligible clusters", p.stderr)


class InstallerTestBase(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="sfm-home-")
        self.fake_src = None

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)
        if self.fake_src:
            shutil.rmtree(self.fake_src, ignore_errors=True)

    def make_fake_source(self, commands=("sfm.md", "sfm-max.md")):
        self.fake_src = tempfile.mkdtemp(prefix="sfm-src-")
        os.makedirs(os.path.join(self.fake_src, "skill", "sfumato"))
        with open(os.path.join(self.fake_src, "skill", "sfumato", "SKILL.md"), "w") as f:
            f.write("skill\n")
        os.makedirs(os.path.join(self.fake_src, "commands"))
        for name in commands:
            with open(os.path.join(self.fake_src, "commands", name), "w") as f:
                f.write(name + "\n")
        with open(os.path.join(self.fake_src, "commands", "notes.txt"), "w") as f:
            f.write("ignored\n")
        return self.fake_src

    def assertCommandsInstalled(self, names):
        cmd_dir = os.path.join(self.home, ".claude", "commands")
        self.assertEqual(sorted(os.listdir(cmd_dir)), sorted(names))
        for n in names:
            with open(os.path.join(cmd_dir, n)) as f:
                self.assertEqual(f.read(), n + "\n")

    RUNTIME_FILES = ("SKILL.md", "references/prompt_templates.md",
                     "resources/domain_pool.json", "scripts/sample_domains.py")
    RETIRED_FILES = ("scripts/check_leak.py",)

    def assertSkillInstalled(self, rel):
        dest = os.path.join(self.home, *rel.split("/"))
        for f in self.RUNTIME_FILES:
            src = os.path.join(REPO, "skill", "sfumato", *f.split("/"))
            self.assertTrue(os.path.isfile(src), src)
            self.assertTrue(os.path.isfile(os.path.join(dest, *f.split("/"))), rel + "/" + f)
        for f in self.RETIRED_FILES:
            src = os.path.join(REPO, "skill", "sfumato", *f.split("/"))
            self.assertFalse(os.path.exists(src), src)
            self.assertFalse(os.path.exists(os.path.join(dest, *f.split("/"))), rel + "/" + f)


@unittest.skipUnless(POWERSHELL, "PowerShell not available")
class InstallPs1Tests(InstallerTestBase):
    SCRIPT = os.path.join(HERE, "install.ps1")

    def _ps(self, *args):
        cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
               "-File", self.SCRIPT, "-HomeDir", self.home] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)

    def test_dry_run_auto_defaults_to_claude_and_writes_nothing(self):
        p = self._ps("-DryRun")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(p.stderr.strip(), "")
        self.assertIn("defaulting to claude", p.stdout)
        self.assertIn("[claude] skill ->", p.stdout)
        self.assertIn("Dry run complete. No files were changed.", p.stdout)
        self.assertEqual(_tree(self.home), [])

    def test_dry_run_all_targets(self):
        p = self._ps("-DryRun", "-Target", "all")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        for t in ("claude", "agy", "codex"):
            self.assertIn("[%s] skill ->" % t, p.stdout)
        self.assertEqual(_tree(self.home), [])

    def test_auto_detects_existing_dirs(self):
        os.makedirs(os.path.join(self.home, ".codex"))
        os.makedirs(os.path.join(self.home, ".gemini"))
        p = self._ps("-DryRun")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("[agy] skill ->", p.stdout)
        self.assertIn("[codex] skill ->", p.stdout)
        self.assertNotIn("[claude]", p.stdout)

    def test_real_install_into_temp_home(self):
        p = self._ps("-Target", "all")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertSkillInstalled(".claude/skills/sfumato")
        self.assertSkillInstalled(".gemini/config/skills/sfumato")
        self.assertSkillInstalled(".codex/skills/sfumato")
        cmd_src = os.path.join(REPO, "commands", "sfm.md")
        self.assertEqual(os.path.isfile(os.path.join(self.home, ".claude", "commands", "sfm.md")),
                         os.path.isfile(cmd_src))
        # reinstall over an existing install must succeed
        p = self._ps("-Target", "claude")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_copies_all_command_files(self):
        src = self.make_fake_source()
        p = self._ps("-Target", "claude", "-Source", src, "-DryRun")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("sfm-max.md", p.stdout)
        self.assertEqual(_tree(self.home), [])
        p = self._ps("-Target", "claude", "-Source", src)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertCommandsInstalled(["sfm.md", "sfm-max.md"])

    def test_invalid_target_rejected(self):
        p = self._ps("-Target", "bogus", "-DryRun")
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(_tree(self.home), [])


def _bash_ok():
    if not BASH:
        return False
    try:
        return subprocess.run([BASH, "-c", "exit 0"], capture_output=True, timeout=30).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


@unittest.skipUnless(_bash_ok(), "bash not available")
class InstallShTests(InstallerTestBase):
    @staticmethod
    def _posix(path):
        path = path.replace("\\", "/")
        if BASH_IS_WSL and len(path) > 1 and path[1] == ":":
            # WSL bash needs /mnt/<drive>/... instead of C:/...
            return "/mnt/" + path[0].lower() + path[2:]
        # Git Bash / MSYS understands forward-slash Windows paths (C:/...).
        return path

    def _sh(self, *args):
        cmd = [BASH, self._posix(os.path.join(HERE, "install.sh")),
               "--home", self._posix(self.home)] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)

    def test_dry_run_writes_nothing(self):
        p = self._sh("--dry-run", "--target", "all")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("Dry run complete. No files were changed.", p.stdout)
        for t in ("claude", "agy", "codex"):
            self.assertIn("[%s] skill ->" % t, p.stdout)
        self.assertEqual(_tree(self.home), [])

    def test_real_install_into_temp_home(self):
        os.makedirs(os.path.join(self.home, ".gemini"))
        p = self._sh()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertSkillInstalled(".gemini/config/skills/sfumato")
        self.assertFalse(os.path.exists(os.path.join(self.home, ".claude", "skills")))

    def test_copies_all_command_files(self):
        src = self._posix(self.make_fake_source())
        p = self._sh("--target", "claude", "--source", src, "--dry-run")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("sfm-max.md", p.stdout)
        self.assertEqual(_tree(self.home), [])
        p = self._sh("--target", "claude", "--source", src)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertCommandsInstalled(["sfm.md", "sfm-max.md"])

    def test_install_sh_is_lf_only(self):
        with open(os.path.join(HERE, "install.sh"), "rb") as f:
            self.assertNotIn(b"\r", f.read())

    def test_invalid_target_rejected(self):
        p = self._sh("--target", "bogus")
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
