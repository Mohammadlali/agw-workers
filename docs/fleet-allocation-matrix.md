# 27-Runner Fleet Allocation Matrix & Task Briefs
## Tri-Cluster Swarm Sprints 1–4 (ACC0–ACC8 | 3 Runners Each)

This document provides concrete task specifications, input parameters, execution contracts, and verification gates for each of the 27 Antigravity CLI runners across the 9 fleet accounts.

---

## Cluster 1: Infrastructure & Automation (ACC0, ACC1, ACC3)

### ACC0 — Mohammadlali (`agw-ACC0`)
- **Account Identity**: `Mohammadlali` (`1997`) | Runner pool: `w01..w03`
- **Sprint Focus**: Sprint 1 Core Daemon

#### `agw-ACC0-w01` — Playwright Cookie Harvester
- **Task**: Implement headless Chromium automation using Playwright to handle Google sign-in and session cookie harvesting.
- **Inputs**: Google account credentials from environment variables (`ACC7_PASS`, `ACC8_PASS`).
- **Target Cookies**: `__Secure-1PSID`, `__Secure-1PSIDTS`.
- **Output**: JSON cookie dictionary containing timestamps and session tokens.
- **Verification Gate**: `python3 Tools/headless_session_refresher.py --mock --all`.

#### `agw-ACC0-w02` — Cookie Sentinel Redirect Detector & Atomic Writer
- **Task**: Implement `Tools/cookie_sentinel.py` redirect loop detection, HTTP 302 detector, and atomic JSON file writer.
- **Schedule**: `*/15 * * * *` cron on 185.204.171.61.
- **Target File**: `/opt/gemini_worker/active_accounts.json`.
- **Concurrency Guard**: Atomic temp-file creation and `os.replace` rename to prevent reader corruption.
- **Verification Gate**: `python3 Tools/cookie_sentinel.py --mock-test`.

#### `agw-ACC0-w03` — Hot-Reload Client & Unit Tests
- **Task**: Implement hot-reload caller for `POST http://127.0.0.1:8085/reload-accounts`.
- **Contract**: Dispatches reload signal upon successful atomic JSON update with a 5-second timeout.
- **Output**: HTTP 200 confirmation or logged warning.
- **Verification Gate**: `python3 Tools/cookie_sentinel.py --reload-only` (or mock equivalent).

---

### ACC1 — Momona (`agw-ACC1`)
- **Account Identity**: `momonakikugava-pixel` (`Momona`) | Runner pool: `w01..w03`
- **Sprint Focus**: Sprint 1 Pool Restoration

#### `agw-ACC1-w01` — Restore Account #7 (`ngocg`)
- **Task**: Restore valid session cookies for account `#7 ngocg` (`ngocgminh5@gmail.com`).
- **Validation**: Confirm `__Secure-1PSID` and `__Secure-1PSIDTS` cookies allow access to `gemini.google.com/app` without 302 redirect.
- **Status Target**: Update account 7 status in `active_accounts.json` from `expired` to `active`.

#### `agw-ACC1-w02` — Restore Account #8 (`lali.94m`)
- **Task**: Restore valid session cookies for account `#8 lali.94m` (`lali.94m@gmail.com`).
- **Validation**: Confirm `__Secure-1PSID` and `__Secure-1PSIDTS` cookies allow access to `gemini.google.com/app` without 302 redirect.
- **Status Target**: Update account 8 status in `active_accounts.json` from `expired` to `active`.

#### `agw-ACC1-w03` — 9/9 Account SNlM0e & BOQ Health Probe
- **Task**: Automated probe querying Gemini session state across all 9 accounts (#0 to #8).
- **Checks**: Presence of `SNlM0e` session auth token and `BOQ` assistant backend response headers.
- **Threshold**: 9/9 green status required for zero-downtime rotation.

---

### ACC3 — ngocg (`agw-ACC3`)
- **Account Identity**: `ngocgminh5-debug` (`ngocg`) | Runner pool: `w01..w03`
- **Sprint Focus**: Sprint 3 Closed-Loop Telemetry

#### `agw-ACC3-w01` — MCP JSON-RPC Telemetry Client
- **Task**: Implement `Tools/mcp_reporter.py` targeting `https://n8n.airboxvip.top/webhook/mcp`.
- **Protocol**: JSON-RPC 2.0 (Protocol `2024-11-05`, `mcp_router_v2.js`).
- **Methods**: `tools/call` for `append_notion_block` and `send_message_to_cookie`.
- **Verification Gate**: `python3 Tools/mcp_reporter.py --dry-run`.

#### `agw-ACC3-w02` — Workflow Hooks in GitHub Actions
- **Task**: Add post-execution reporting hooks in `.github/workflows/agw-worker.yml` and `agy-lead-plan.yml`.
- **Safety**: Pass all inputs through `env:` to avoid run-body injection.
- **Verification Gate**: `python3 Tools/check_run_injection.py .github/workflows`.

#### `agw-ACC3-w03` — E2E Synchronization with n8n
- **Task**: Verify event synchronization with n8n workflows `9AefIVy4aHRcna2W` (Issue Close → Notion Done) and `xzBR15arXeESLvYJ`.
- **Output**: End-to-end receipt confirmation from n8n webhook gateway.

---

## Cluster 2: AI Lead Generation & CRM (ACC2)

### ACC2 — lali.94m (`agw-ACC2`)
- **Account Identity**: `lali94m-max` (`lali.94m`) | Runner pool: `w01..w03`
- **Sprint Focus**: Sprint 2 AI Lead Hunter Auto-Proposal Generator

#### `agw-ACC2-w01` — Telegram Callback Router
- **Task**: Intercept Telegram inline button callback `[🚀 Send AI Proposal]` from VIP lead channel.
- **Route**: Webhook `RdtBCbtFClRbiB8U`.
- **Output**: Trigger proposal generation pipeline for the clicked lead ID.

#### `agw-ACC2-w02` — Notion CRM Reader & Gemini 4 Argon Prompt
- **Task**: Read lead requirements from Notion CRM DB `3f9befc7-ddfb-8119-a549-d0934e6e8a12` and invoke Gemini 4 Argon.
- **Format**: Bilingual technical proposal (English summary + Persian scope and timeline).
- **Verification Gate**: `python3 Tools/lead_hunter_proposal.py --mock`.

#### `agw-ACC2-w03` — One-Click Telegram Staging & Plan: false Guard
- **Task**: Append generated proposal to Notion while asserting that the `Plan` checkbox is `false`.
- **Safety**: The `Plan: false` guard prevents accidental triggering of fleet-wide batch planning workflows.
- **Telegram Staging**: Format inline confirmation keyboard for single-click executive dispatch.

---

## Cluster 3: Game Engine & Vertical Slice (ACC4, ACC5, ACC7, ACC8)

### ACC4 — lets (`agw-ACC4`)
- **Account Identity**: `hmmletssee7-design` (`lets`) | Runner pool: `w01..w03`
- **Sprint Focus**: Sprint 4A Character Pipeline

#### `agw-ACC4-w01` — Import Kaveh 3D Turnaround into `TBS-M04`
- **Task**: Ingest `zahra_1792003384_image.jpg` 3D turnaround reference and bind mesh coordinates to Godot module `TBS-M04`.
- **Output**: Character model rig and initial 3D turnaround scene in Godot 4.3.

#### `agw-ACC4-w02` — Morad Cyber-Barista Sprite Sheet Integration
- **Task**: Slice and animate Morad Cyber-Barista 2D sprite sheets.
- **Animations**: Idle, pouring espresso, conversation dialogue poses.
- **Target Module**: `TBS-M04`.

#### `agw-ACC4-w03` — Asset Integrity Gate (Magic Bytes & SHA-256)
- **Task**: Validate binary headers for all media assets:
  - JPEG/JFIF: `\xff\xd8\xff`
  - PNG: `\x89PNG\r\n\x1a\n`
- **Verification Gate**: `python3 Tools/check_tbs_assets.py`.

---

### ACC5 — Just (`agw-ACC5`)
- **Account Identity**: `kidding602` (`Just`) | Runner pool: `w01..w03`
- **Sprint Focus**: Sprint 4B Parchak Café 3D Scene

#### `agw-ACC5-w01` — Exterior Facade & Signboard Textures
- **Task**: Bind Parchak Cheese Café 3/3 exterior textures and signboard materials in Godot module `TBS-M05`.
- **Target Asset**: `TBS-M15` / `488babe2-d9f1-4f48-8b1c-3df7d7ddbbf1`.

#### `agw-ACC5-w02` — Interior Collision & Navigation Meshes
- **Task**: Configure static body 3D collisions, counter obstacles, and NPC navigation polygon meshes.
- **Target Module**: `TBS-M05`.

#### `agw-ACC5-w03` — Touch Input & Camera Rig Bounds
- **Task**: Link `TBS-M01` mobile touch gesture routing to `TBS-M03` camera rig viewport constraints.
- **Output**: Responsive camera clamping and pinch-to-zoom bounds within the café interior.

---

### ACC7 — M2 (`agw-ACC7`)
- **Account Identity**: `mohammad97okk` (`M2`) | Runner pool: `w01..w03`
- **Sprint Focus**: Sprint 4C Ren'Py Dialogue & RTL Localization

#### `agw-ACC7-w01` — Persian RTL Dialogue Trees
- **Task**: Author Ren'Py 8.5.3 dialogue trees with native Persian RTL text rendering (`config.rtl = True`).
- **Localization**: High-fidelity typography, Arabic shaping, and bi-directional numeral handling.
- **Verification Gate**: `python3 Tools/check_tbs_assets.py`.

#### `agw-ACC7-w02` — Event Bus & Player Controller Triggers
- **Task**: Connect dialogue branch completions to Godot `TBS-M00` Event Bus and `TBS-M02` Player Controller state machine.
- **Output**: Seamless handoff between narrative dialogue scenes and playable 3D navigation.

#### `agw-ACC7-w03` — Composition Root & SQLite State Sync
- **Task**: Implement `TBS-M06` Composition Root and local SQLite persistence for player inventory, café orders, and quest states.

---

### ACC8 — zahra (`agw-ACC8`)
- **Account Identity**: `moradzahra85-png` (`zahra`) | Runner pool: `w01..w03`
- **Sprint Focus**: Sprint 4D Vertical Slice QA & Packaging

#### `agw-ACC8-w01` — Full Vertical Slice Scene Integration
- **Task**: Integrate modules `TBS-M00` through `TBS-M06` into a single cohesive, playable scene loop.
- **Flow**: Café entrance -> Dialogue with Morad -> Order Cheese Toast -> Explore 3D café floor.

#### `agw-ACC8-w02` — Headless Godot 4.3 / Ren'Py Automated Tests & APK Build
- **Task**: Run headless automated test suite for Godot 4.3 scenes and execute Android APK compilation check.
- **Checks**: Zero memory leaks, zero unresolved Node paths, 60fps frame timing baseline.

#### `agw-ACC8-w03` — Gate Transcript Generation for ACC6
- **Task**: Export structured JSON gate transcripts and execution metrics formatted for consumption by ACC6 Master Aggregator.

---

## Master Aggregator (ACC6)

### ACC6 — 07 (`agw-ACC6`)
- **Account Identity**: `mohammadlali0707-stack` (`07`) | Runner pool: `w01..w03`
- **Role**: **Strictly Untasked from Implementation — Master Aggregator & QA Gates Only**

#### `agw-ACC6-w01` — Output Collector
- **Task**: Collect and catalogue output transcripts from all 24 active worker runners across `ACC0`–`ACC5`, `ACC7`–`ACC8`.
- **Target**: `Reports/agy/acc{0..8}/*.txt`.

#### `agw-ACC6-w02` — Gate Runner
- **Task**: Execute `Tools/run_gates.py` and `Tools/check_changelog.py`.
- **Requirement**: Enforce 10/10 quality gates pass before authorizing final fleet report publication.

#### `agw-ACC6-w03` — Fleet Report Compiler & Notion Synchronizer
- **Task**: Compile unified Fleet Report markdown document (`Reports/agy/fleet_report_sprints_1_4.md`) and sync final execution summary to Notion Task Card `3f9befc7-ddfb-81ea-b452-e64d1df11f2f`.
- **Verification Gate**: `python3 Tools/fleet_summarizer.py`.
