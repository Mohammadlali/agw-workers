#!/usr/bin/env python3
"""Unified Quality Gate Runner for agw-workers.

Executed by ACC6 Aggregator runner 'w02':
"Run 'Tools/run_gates.py' & 'check_changelog.py'"

Consolidates all CI gates, workflow safety checks, and architecture probes.
"""

import glob
import json
import os
import re
import subprocess
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS_DIR = os.path.join(REPO_ROOT, ".github", "workflows")


def log_section(title: str):
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")


def check_crlf() -> tuple[bool, str]:
    crlf_files = []
    for root, _, files in os.walk(WORKFLOWS_DIR):
        for f in files:
            if f.endswith((".yml", ".yaml")):
                p = os.path.join(root, f)
                with open(p, "rb") as fh:
                    if b"\r" in fh.read():
                        crlf_files.append(os.path.relpath(p, REPO_ROOT))
    if crlf_files:
        return False, f"CRLF endings found in: {', '.join(crlf_files)}"
    return True, "No CRLF endings found"


def check_yaml_syntax() -> tuple[bool, str]:
    bad_files = []
    files = sorted(glob.glob(os.path.join(WORKFLOWS_DIR, "*.yml")) + glob.glob(os.path.join(WORKFLOWS_DIR, "*.yaml")))
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            if not isinstance(data, dict):
                continue
            for jname, jbody in (data.get("jobs") or {}).items():
                if not jbody or not jbody.get("steps"):
                    bad_files.append(f"{os.path.basename(fp)} (job '{jname}' has no steps)")
        except Exception as e:
            bad_files.append(f"{os.path.basename(fp)}: {e}")
    if bad_files:
        return False, f"YAML errors: {'; '.join(bad_files)}"
    return True, f"All {len(files)} workflow files have valid YAML syntax and non-empty jobs"


def check_heredoc_backticks() -> tuple[bool, str]:
    _HEREDOC_START = re.compile(r"<<\s*([A-Za-z_][A-Za-z0-9_]*)\b")
    _HEREDOC_QUOTED = re.compile(r"<<\s*['\\\"]")
    files = sorted(glob.glob(os.path.join(WORKFLOWS_DIR, "*.yml")) + glob.glob(os.path.join(WORKFLOWS_DIR, "*.yaml")))
    errors = []

    for fp in files:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        in_heredoc = False
        delimiter = None
        for i, raw in enumerate(lines, 1):
            line = raw.rstrip("\n")
            if not in_heredoc:
                if _HEREDOC_QUOTED.search(line):
                    continue
                m = _HEREDOC_START.search(line)
                if m:
                    in_heredoc = True
                    delimiter = m.group(1)
            else:
                if line.strip() == delimiter:
                    in_heredoc = False
                    delimiter = None
                    continue
                col = 0
                while col < len(line):
                    if line[col] == "\\":
                        col += 2
                        continue
                    if line[col] == "`":
                        errors.append(f"{os.path.basename(fp)}:{i} (unescaped backtick in heredoc)")
                        break
                    col += 1
    if errors:
        return False, f"Heredoc backtick violations: {'; '.join(errors)}"
    return True, "No unescaped backticks in unquoted heredocs"


def check_runs_on_policy() -> tuple[bool, str]:
    must_be_hosted = {"gate-webhook-health.yml", "gate-runs-on-policy.yml", "gate-yaml-lint.yml"}
    hosted_prefixes = ("ubuntu-", "windows-", "macos-")
    violations = []
    seen = set()

    for fp in glob.glob(os.path.join(WORKFLOWS_DIR, "*.yml")):
        name = os.path.basename(fp)
        if name not in must_be_hosted:
            continue
        seen.add(name)
        with open(fp, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        for jname, job in (doc.get("jobs") or {}).items():
            runs_on = str(job.get("runs-on", ""))
            if not runs_on.startswith(hosted_prefixes):
                violations.append(f"{name} [{jname}] runs-on: {runs_on}")

    missing = must_be_hosted - seen
    if missing:
        violations.append(f"Missing monitors: {', '.join(missing)}")
    if violations:
        return False, f"runs-on violations: {'; '.join(violations)}"
    return True, "All protected monitors run on GitHub-hosted runners"


def run_subtool(command: list[str], name: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(command, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        output = proc.stdout.strip()
        last_line = output.splitlines()[-1] if output else ""
        return proc.returncode == 0, f"{name}: {'PASS' if proc.returncode == 0 else 'FAIL'} - {last_line}"
    except Exception as e:
        return False, f"{name} execution error: {e}"


def main():
    log_section("ACC6 MASTER AGGREGATOR — REPOSITORY GATE RUNNER")
    results = {}

    # Gate 1: CRLF
    ok1, msg1 = check_crlf()
    results["crlf"] = ok1
    print(f"[{'PASS' if ok1 else 'FAIL'}] CRLF Line Endings: {msg1}")

    # Gate 2: YAML Syntax
    ok2, msg2 = check_yaml_syntax()
    results["yaml_syntax"] = ok2
    print(f"[{'PASS' if ok2 else 'FAIL'}] YAML Syntax & Structure: {msg2}")

    # Gate 3: Heredoc Backticks
    ok3, msg3 = check_heredoc_backticks()
    results["heredoc_backticks"] = ok3
    print(f"[{'PASS' if ok3 else 'FAIL'}] Heredoc Backticks: {msg3}")

    # Gate 4: Runs-on Policy
    ok4, msg4 = check_runs_on_policy()
    results["runs_on_policy"] = ok4
    print(f"[{'PASS' if ok4 else 'FAIL'}] runs-on Policy: {msg4}")

    # Gate 5: Job env contexts
    ok5, msg5 = run_subtool([sys.executable, "Tools/check_job_env_contexts.py", ".github/workflows"], "job_env_contexts")
    results["job_env_contexts"] = ok5
    print(f"[{'PASS' if ok5 else 'FAIL'}] {msg5}")

    # Gate 6: Run injection
    ok6, msg6 = run_subtool([sys.executable, "Tools/check_run_injection.py", ".github/workflows"], "run_injection")
    results["run_injection"] = ok6
    print(f"[{'PASS' if ok6 else 'FAIL'}] {msg6}")

    # Gate 7: Changelog validator
    ok7, msg7 = run_subtool([sys.executable, "Tools/check_changelog.py"], "check_changelog")
    results["check_changelog"] = ok7
    print(f"[{'PASS' if ok7 else 'FAIL'}] {msg7}")

    # Gate 8: TBS Assets & Architecture
    ok8, msg8 = run_subtool([sys.executable, "Tools/check_tbs_assets.py"], "check_tbs_assets")
    results["tbs_assets"] = ok8
    print(f"[{'PASS' if ok8 else 'FAIL'}] {msg8}")

    # Gate 9: Cookie Sentinel mock test
    ok9, msg9 = run_subtool([sys.executable, "Tools/cookie_sentinel.py", "--mock-test"], "cookie_sentinel")
    results["cookie_sentinel"] = ok9
    print(f"[{'PASS' if ok9 else 'FAIL'}] {msg9}")

    # Gate 10: MCP Telemetry Client test
    ok10, msg10 = run_subtool([sys.executable, "Tools/mcp_reporter.py", "--dry-run", "--account", "6", "--tag", "acc6-gate-test"], "mcp_reporter")
    results["mcp_reporter"] = ok10
    print(f"[{'PASS' if ok10 else 'FAIL'}] {msg10}")

    all_passed = all(results.values())
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    log_section(f"GATE SUMMARY: {passed_count}/{total_count} PASSED")
    print("##TBS##" + json.dumps({
        "probe": "run_gates",
        "status": "pass" if all_passed else "fail",
        "v": 1,
        "data": {
            "total_gates": total_count,
            "passed_gates": passed_count,
            "details": results,
        }
    }))

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
