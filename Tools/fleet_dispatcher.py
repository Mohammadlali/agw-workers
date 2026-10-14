#!/usr/bin/env python3
"""Tri-Cluster Swarm Fleet Dispatcher.

Parses and validates dispatch directives matching:
/dispatch --slot all --accounts ACC0,ACC1,ACC2,ACC3,ACC4,ACC5,ACC7,ACC8 --summarizer ACC6 --runners 27
"""

import argparse
import json
import sys

FLEET_MATRIX = {
    "ACC0": {
        "identity": "Mohammadlali (1997)",
        "runners": ["agw-ACC0-w01", "agw-ACC0-w02", "agw-ACC0-w03"],
        "sprint": "Sprint 1 Core Daemon",
        "deliverables": [
            "w01: Playwright cookie harvester",
            "w02: cookie_sentinel.py redirect detector & atomic JSON writer",
            "w03: /reload-accounts hot-reload client & unit tests",
        ],
    },
    "ACC1": {
        "identity": "momonakikugava-pixel (Momona)",
        "runners": ["agw-ACC1-w01", "agw-ACC1-w02", "agw-ACC1-w03"],
        "sprint": "Sprint 1 Pool Restoration",
        "deliverables": [
            "w01: Restore #7 ngocg",
            "w02: Restore #8 lali.94m",
            "w03: 9/9 account SNlM0e & BOQ health probe",
        ],
    },
    "ACC2": {
        "identity": "lali94m-max (lali.94m)",
        "runners": ["agw-ACC2-w01", "agw-ACC2-w02", "agw-ACC2-w03"],
        "sprint": "Sprint 2 Lead Hunter UI",
        "deliverables": [
            "w01: [🚀 Send AI Proposal] Telegram callback router",
            "w02: Notion CRM reader & Argon proposal prompt",
            "w03: One-click Telegram staging & Plan: false guard",
        ],
    },
    "ACC3": {
        "identity": "ngocgminh5-debug (ngocg)",
        "runners": ["agw-ACC3-w01", "agw-ACC3-w02", "agw-ACC3-w03"],
        "sprint": "Sprint 3 Closed-Loop Telemetry",
        "deliverables": [
            "w01: MCP JSON-RPC append_notion_block client",
            "w02: Workflow hooks in agw-worker.yml",
            "w03: E2E sync with n8n 9AefIVy4aHRcna2W & xzBR15arXeESLvYJ",
        ],
    },
    "ACC4": {
        "identity": "hmmletssee7-design (lets)",
        "runners": ["agw-ACC4-w01", "agw-ACC4-w02", "agw-ACC4-w03"],
        "sprint": "Sprint 4A Character Pipeline",
        "deliverables": [
            "w01: Import Kaveh 3D turnaround into TBS-M04",
            "w02: Morad Cyber-Barista sprite sheet integration",
            "w03: Asset hash & JFIF/PNG magic-byte gate checks",
        ],
    },
    "ACC5": {
        "identity": "kidding602 (Just)",
        "runners": ["agw-ACC5-w01", "agw-ACC5-w02", "agw-ACC5-w03"],
        "sprint": "Sprint 4B Parchak Café 3D Scene",
        "deliverables": [
            "w01: Bind Exterior Facade & Signboard textures in TBS-M05",
            "w02: Interior collision & nav meshes",
            "w03: TBS-M01 Touch & TBS-M03 Camera Rig bounds",
        ],
    },
    "ACC6": {
        "identity": "mohammadlali0707-stack (07)",
        "runners": ["agw-ACC6-w01", "agw-ACC6-w02", "agw-ACC6-w03"],
        "sprint": "Untasked Aggregator",
        "deliverables": [
            "w01: Collect outputs from all 24 worker runners (ACC0–ACC5, ACC7–ACC8)",
            "w02: Run Tools/run_gates.py & check_changelog.py",
            "w03: Compile final Fleet Report & sync to Notion Page 3f9befc7-ddfb-81ea-b452-e64d1df11f2f",
        ],
    },
    "ACC7": {
        "identity": "mohammad97okk (M2)",
        "runners": ["agw-ACC7-w01", "agw-ACC7-w02", "agw-ACC7-w03"],
        "sprint": "Sprint 4C Ren'Py Dialogue",
        "deliverables": [
            "w01: Persian RTL dialogue trees (config.rtl = True)",
            "w02: TBS-M00 Event Bus & TBS-M02 Player Controller triggers",
            "w03: TBS-M06 Composition Root & SQLite sync",
        ],
    },
    "ACC8": {
        "identity": "moradzahra85-png (zahra)",
        "runners": ["agw-ACC8-w01", "agw-ACC8-w02", "agw-ACC8-w03"],
        "sprint": "Sprint 4D Vertical Slice QA",
        "deliverables": [
            "w01: Full vertical slice scene integration",
            "w02: Headless Godot 4.3/Ren'Py automated tests & APK build check",
            "w03: Gate transcript generation for ACC6",
        ],
    },
}


def parse_dispatch_directive(args_list: list[str]) -> dict:
    parser = argparse.ArgumentParser(prog="/dispatch")
    parser.add_argument("--slot", default="all")
    parser.add_argument("--accounts", required=True)
    parser.add_argument("--summarizer", required=True)
    parser.add_argument("--runners", type=int, default=27)

    parsed = parser.parse_args(args_list)
    worker_accounts = [a.strip() for a in parsed.accounts.split(",") if a.strip()]

    # Verification rules
    assert parsed.summarizer == "ACC6", f"Summarizer must be ACC6, got {parsed.summarizer}"
    assert "ACC6" not in worker_accounts, "ACC6 must remain untasked from implementation"
    assert "ACC9" not in worker_accounts, "ACC9 is permanently retired"

    total_expected = len(worker_accounts) * 3 + 3  # 24 + 3 = 27
    assert parsed.runners == total_expected, f"Runner count mismatch: expected {total_expected}, got {parsed.runners}"

    plan = {
        "status": "validated",
        "slot_mode": parsed.slot,
        "worker_accounts": worker_accounts,
        "worker_runner_count": len(worker_accounts) * 3,
        "summarizer_account": parsed.summarizer,
        "summarizer_runner_count": 3,
        "total_runners": parsed.runners,
        "roster": {acc: FLEET_MATRIX[acc] for acc in worker_accounts + [parsed.summarizer]},
    }
    return plan


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "/dispatch":
        raw_args = sys.argv[2:]
    else:
        raw_args = sys.argv[1:]

    if not raw_args:
        raw_args = [
            "--slot", "all",
            "--accounts", "ACC0,ACC1,ACC2,ACC3,ACC4,ACC5,ACC7,ACC8",
            "--summarizer", "ACC6",
            "--runners", "27"
        ]

    plan = parse_dispatch_directive(raw_args)
    print(f"✅ Dispatch Directive Validated: {plan['total_runners']} Runners allocated across {len(plan['worker_accounts']) + 1} Accounts.")
    print(f"Workers: {', '.join(plan['worker_accounts'])} (24 runners)")
    print(f"Summarizer: {plan['summarizer_account']} (3 runners)")
    print("##TBS##" + json.dumps({
        "probe": "fleet_dispatch",
        "status": "pass",
        "v": 1,
        "data": {
            "total_runners": plan["total_runners"],
            "worker_runners": plan["worker_runner_count"],
            "summarizer": plan["summarizer_account"],
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
