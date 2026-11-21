#!/usr/bin/env python3
"""Tests for tools/summarize_benchmarks.py and the installers (stdlib only).

Run: python tools/test_tools.py
Installer tests never touch the real home directory: they pass an explicit
temporary home (-HomeDir / --home). Tests are skipped when the shell is absent.
"""
from __future__ import annotations

import contextlib
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


class InstallerTestBase(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="sfm-home-")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def assertSkillInstalled(self, rel):
        dest = os.path.join(self.home, *rel.split("/"))
        for f in ("SKILL.md", "references/prompt_templates.md", "resources/domain_pool.json",
                  "scripts/sample_domains.py"):
            src = os.path.join(REPO, "skill", "sfumato", *f.split("/"))
            if os.path.exists(src):
                self.assertTrue(os.path.isfile(os.path.join(dest, *f.split("/"))), rel + "/" + f)


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

    def test_invalid_target_rejected(self):
        p = self._sh("--target", "bogus")
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
