# Software Design Specification (SDD) & Task Brief: Tri-Cluster Swarm Sprints 1–4
## 27 AGY Runners | ACC0–ACC8 Fleet Architecture & ACC6 Master Aggregator

- **Notion Task Card**: [CCP SDD & Task Brief: Tri-Cluster Sprints 1–4](https://app.notion.com/p/CCP-SDD-Task-Brief-Tri-Cluster-Sprints-1-4-27-AGY-Runners-ACC0-ACC8-ACC6-Summarizer-Plan-O-3f9befc7ddfb81eab452e64d1df11f2f) (`3f9befc7-ddfb-81ea-b452-e64d1df11f2f`)
- **Control-Room Master Issue**: [Control-Room #19](https://github.com/mohammadlali0707-stack/Control-Room/issues/19)
- **Notion Task Board DB**: `3dcbefc7-ddfb-80e1-8e26-ced6033af37f`
- **MCP Gateway Endpoint**: `https://n8n.airboxvip.top/webhook/mcp` (`mcp_router_v2.js` | Protocol `2024-11-05`)
- **Fleet Topology**: **27 Antigravity CLI Runners** across **9 GitHub Accounts (`ACC0` to `ACC8`, 3 runners per account: `w01..w03`)**
  - **Active Workload (24 Runners)**: `ACC0`, `ACC1`, `ACC2`, `ACC3`, `ACC4`, `ACC5`, `ACC7`, `ACC8` (3 CLI runners each)
  - **Untasked Aggregator (`ACC6` / `07`)**: **Strictly NOT tasked with implementation**; dedicated exclusively to output collection, running `Tools/run_gates.py`, and publishing the unified Fleet Report.

---

## 1. System Architecture & Topology

```
+---------------------------------------------------------------------------------------------------+
|                               TRI-CLUSTER SWARM FLEET (27 RUNNERS)                                |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ Cluster 1: Infrastructure & Automation ]                                                      |
|    - ACC0 (Mohammadlali): Sprint 1 Core Daemon (Playwright, Sentinel, Hot Reload)   [w01..w03]    |
|    - ACC1 (Momona):       Sprint 1 Pool Restoration (#7 ngocg, #8 lali.94m)        [w01..w03]    |
|    - ACC3 (ngocg):        Sprint 3 Closed-Loop Telemetry (MCP JSON-RPC, n8n)        [w01..w03]    |
|                                                                                                   |
|  [ Cluster 2: AI Lead Generation & CRM ]                                                          |
|    - ACC2 (lali.94m):     Sprint 2 Lead Hunter UI ([🚀 Send AI Proposal], Notion)   [w01..w03]    |
|                                                                                                   |
|  [ Cluster 3: Game Engine & Vertical Slice (CCP / TBS) ]                                         |
|    - ACC4 (lets):         Sprint 4A Character Pipeline (Kaveh 3D, Morad Sprites)    [w01..w03]    |
|    - ACC5 (Just):         Sprint 4B Parchak Café 3D Scene (Godot TBS-M05)          [w01..w03]    |
|    - ACC7 (M2):           Sprint 4C Ren'Py Dialogue (Persian RTL config.rtl=True)   [w01..w03]    |
|    - ACC8 (zahra):        Sprint 4D Vertical Slice QA (Integration, APK Check)      [w01..w03]    |
|                                                                                                   |
|  [ Master Aggregator & Relay Host ]                                                               |
|    - ACC6 (07):           Untasked Aggregator (Output Collect, run_gates, Report)   [w01..w03]    |
+---------------------------------------------------------------------------------------------------+
```

### 1.1 Account-to-Identity Mapping
| Index | GitHub Account | Identity Label | Role | Runner Allocation |
|---|---|---|---|---|
| **ACC0** | `Mohammadlali` | `1997` | Sprint 1 Core Daemon & Gist Owner | `agw-ACC0-w01..w03` |
| **ACC1** | `momonakikugava-pixel` | `Momona` | Sprint 1 Pool Restoration | `agw-ACC1-w01..w03` |
| **ACC2** | `lali94m-max` | `lali.94m` | Sprint 2 AI Lead Hunter UI | `agw-ACC2-w01..w03` |
| **ACC3** | `ngocgminh5-debug` | `ngocg` | Sprint 3 Closed-Loop Telemetry | `agw-ACC3-w01..w03` |
| **ACC4** | `hmmletssee7-design` | `lets` | Sprint 4A Character Pipeline | `agw-ACC4-w01..w03` |
| **ACC5** | `kidding602` | `Just` | Sprint 4B Parchak Café 3D Scene | `agw-ACC5-w01..w03` |
| **ACC6** | `mohammadlali0707-stack` | `07` | **Master Aggregator & Relay Host** | `agw-ACC6-w01..w03` |
| **ACC7** | `mohammad97okk` | `M2` | Sprint 4C Ren'Py Persian Dialogue | `agw-ACC7-w01..w03` |
| **ACC8** | `moradzahra85-png` | `zahra` | Sprint 4D Vertical Slice QA | `agw-ACC8-w01..w03` |
| **ACC9** | `stranger77777777` | *(Retired)* | Permanently retired; never used | *(None)* |

---

## 2. Sprint Specifications (Sprints 1 to 4)

### Sprint 1: Headless Automated Session Refresher (`185.204.171.61:8085`)
- **Objective**: Maintain uninterrupted 9/9 account rotation for ~7,000+ daily multimodal queries against Gemini Web API.
- **Problem**: Accounts `#7 ngocg` (`ngocgminh5@gmail.com`) and `#8 lali.94m` (`lali.94m@gmail.com`) encounter cookie expiration (`__Secure-1PSID` and `__Secure-1PSIDTS`), dropping rotation capacity to 7/9.
- **Architecture**:
  1. **`cookie_sentinel.py`** runs as a systemd cron daemon on `*/15 * * * *`.
  2. Sends lightweight HEAD/GET request to `https://gemini.google.com/app`.
  3. Detects HTTP 302/303 redirect to `accounts.google.com/signin/v2` or missing `SNlM0e` / `BOQ` payload markers.
  4. Triggers **`headless_session_refresher.py`** (Chromium / Playwright) with isolated user-data directories.
  5. Harvests fresh `__Secure-1PSID` and `__Secure-1PSIDTS` cookies.
  6. Atomically updates `/opt/gemini_worker/active_accounts.json` using a temporary file + atomic `os.replace` to eliminate file-lock contention.
  7. Calls `POST http://127.0.0.1:8085/reload-accounts` for zero-downtime hot reloading of the rotation pool.

### Sprint 2: AI Lead Hunter Auto-Proposal Generator (`RdtBCbtFClRbiB8U`)
- **Objective**: Convert inbound Telegram VIP lead alerts into structured technical proposals within seconds.
- **Workflow**:
  1. Telegram VIP lead alert includes an inline callback button: `[🚀 Send AI Proposal]`.
  2. Clicking the button triggers n8n webhook route `RdtBCbtFClRbiB8U`.
  3. Lead details fetched from Notion CRM Database `3f9befc7-ddfb-8119-a549-d0934e6e8a12`.
  4. Prompt constructed and dispatched to **Gemini 4 Argon**.
  5. Proposal returned in bilingual format (Executive English summary + RTL Persian technical scope).
  6. Proposal appended to Notion task page while strictly enforcing **`Plan: false` guard** (preventing unintentional trigger of fleet-wide batch planning).
  7. Stages one-click Telegram dispatch with confirmation keyboard for executive signoff.

### Sprint 3: Closed-Loop AGY Runner Reporting (`agw-workers` → MCP → Notion)
- **Objective**: Complete bidirectional event feedback between AGY GitHub Actions runners and central Notion management.
- **Protocol**: MCP (Model Context Protocol) JSON-RPC 2.0 (Protocol `2024-11-05`, `mcp_router_v2.js`).
- **Endpoint**: `https://n8n.airboxvip.top/webhook/mcp`
- **Payload Schema**:
  ```json
  {
    "jsonrpc": "2.0",
    "id": "notion-run-<id>",
    "method": "tools/call",
    "params": {
      "name": "append_notion_block",
      "arguments": {
        "page_id": "3f9befc7-ddfb-81ea-b452-e64d1df11f2f",
        "block_type": "callout",
        "run_id": "${GITHUB_RUN_ID}",
        "account": "ACC3",
        "issue_number": "${ISSUE_NUMBER}",
        "status": "success",
        "summary": "Runner completed execution..."
      }
    }
  }
  ```
- **Workflow Integrations**:
  - `.github/workflows/agw-worker.yml`: Added post-execution hook calling `Tools/mcp_reporter.py` upon job completion.
  - `.github/workflows/agy-lead-plan.yml`: Added post-execution hook calling `Tools/mcp_reporter.py` upon lead plan completion.
  - Integrates with n8n workflows `9AefIVy4aHRcna2W` (Issue Close → Notion Done) and `xzBR15arXeESLvYJ`.

### Sprint 4: Claud-Cloud-Project (CCP / TBS) Playable Vertical Slice Integration
- **Objective**: Assemble a playable vertical slice combining 3D environment exploration, character sprites, and bilingual dialogue.
- **Assets Ingested**:
  - Kaveh 3D turnaround: `zahra_1792003384_image.jpg` (JPEG header `\xff\xd8\xff`).
  - Morad Cyber-Barista sprite sheets (`morad_cyber_barista.png`, PNG header `\x89PNG\r\n\x1a\n`).
  - Parchak Cheese Café 3/3 assets (`TBS-M15` / `488babe2-d9f1-4f48-8b1c-3df7d7ddbbf1`).
- **Modular Godot 4.3 Architecture (`TBS-M00` through `TBS-M06`)**:
  - `TBS-M00`: Event Bus & Signal Orchestration.
  - `TBS-M01`: Touch Input & Mobile Gesture Router.
  - `TBS-M02`: Player Controller & State Machine.
  - `TBS-M03`: Camera Rig & Dynamic Viewport Bounds.
  - `TBS-M04`: Character Pipeline (Kaveh 3D turnaround & Morad sprites).
  - `TBS-M05`: Parchak Cheese Café 3D Scene (Exterior facade & signboard collision).
  - `TBS-M06`: Composition Root & SQLite Local State.
- **Ren'Py 8.5.3 Localization**:
  - Full Persian RTL dialogue trees configured with `config.rtl = True`.
  - Event triggers bound between Ren'Py dialogue completion and Godot `TBS-M00` event bus.

---

## 3. 27-Runner Fleet Allocation Matrix (`ACC0` to `ACC8`)

| Account | Identity | Runners | Sprint Assignment | Concrete Deliverables & Acceptance Gates |
| :--- | :--- | :--- | :--- | :--- |
| **ACC0** | `Mohammadlali` | `agw-ACC0-w01` | Sprint 1 | **Playwright Cookie Harvester**: Headless Chromium daemon capturing `__Secure-1PSID` & `__Secure-1PSIDTS`. |
| | | `agw-ACC0-w02` | Sprint 1 | **Cookie Sentinel Daemon**: `*/15 * * * *` redirect detector and atomic JSON writer for `/opt/gemini_worker/active_accounts.json`. |
| | | `agw-ACC0-w03` | Sprint 1 | **Hot Reload Client & Tests**: Unit tests and caller for `POST http://127.0.0.1:8085/reload-accounts`. |
| **ACC1** | `momonakikugava-pixel` | `agw-ACC1-w01` | Sprint 1 | **Account #7 Restoration**: Live cookie restoration for `ngocgminh5@gmail.com`. |
| | | `agw-ACC1-w02` | Sprint 1 | **Account #8 Restoration**: Live cookie restoration for `lali.94m@gmail.com`. |
| | | `agw-ACC1-w03` | Sprint 1 | **9/9 Rotation Health Probe**: Automated verification of `SNlM0e` & `BOQ` tokens across all 9 accounts. |
| **ACC2** | `lali94m-max` | `agw-ACC2-w01` | Sprint 2 | **Telegram Callback Router**: Handling `[🚀 Send AI Proposal]` webhook events from VIP channel alerts. |
| | | `agw-ACC2-w02` | Sprint 2 | **Notion CRM & Argon Prompt**: Context fetcher from DB `3f9befc7-ddfb-8119-a549-d0934e6e8a12` and Gemini 4 Argon prompt generation. |
| | | `agw-ACC2-w03` | Sprint 2 | **One-Click Staging & Plan Guard**: One-click Telegram confirmation dispatch with mandatory `Plan: false` guard. |
| **ACC3** | `ngocgminh5-debug` | `agw-ACC3-w01` | Sprint 3 | **MCP JSON-RPC Client**: Implementation of `Tools/mcp_reporter.py` (Protocol `2024-11-05`, `append_notion_block`). |
| | | `agw-ACC3-w02` | Sprint 3 | **Workflow Hooks**: Adding closed-loop telemetry steps in `agw-worker.yml` and `agy-lead-plan.yml`. |
| | | `agw-ACC3-w03` | Sprint 3 | **n8n E2E Synchronization**: Integration testing with n8n workflows `9AefIVy4aHRcna2W` and `xzBR15arXeESLvYJ`. |
| **ACC4** | `hmmletssee7-design` | `agw-ACC4-w01` | Sprint 4A | **Kaveh 3D Turnaround**: Importing and rigging `zahra_1792003384_image.jpg` into `TBS-M04`. |
| | | `agw-ACC4-w02` | Sprint 4A | **Morad Cyber-Barista Sprites**: Multi-frame sprite sheet integration and state animation. |
| | | `agw-ACC4-w03` | Sprint 4A | **Asset Integrity Gate**: Automated verification of SHA-256 hashes and JFIF/PNG magic-bytes. |
| **ACC5** | `kidding602` | `agw-ACC5-w01` | Sprint 4B | **Exterior Facade & Textures**: Texture mapping and signboard binding in `TBS-M05`. |
| | | `agw-ACC5-w02` | Sprint 4B | **Interior Collision & Navmesh**: Godot 4.3 physics collision bounds and navigation meshes. |
| | | `agw-ACC5-w03` | Sprint 4B | **Input & Camera Rig Bounds**: Binding `TBS-M01` touch gesture router to `TBS-M03` camera bounds. |
| **ACC6** | `mohammadlali0707-stack` | `agw-ACC6-w01` | Aggregator | **Output Collection**: Aggregating raw output reports from all 24 worker runners (`ACC0–ACC5`, `ACC7–ACC8`). |
| | | `agw-ACC6-w02` | Aggregator | **Master Gate Execution**: Running `Tools/run_gates.py` and `Tools/check_changelog.py` across repository. |
| | | `agw-ACC6-w03` | Aggregator | **Fleet Report & Notion Sync**: Compiling final Fleet Report and syncing to Notion Page `3f9befc7-ddfb-81ea-b452-e64d1df11f2f`. |
| **ACC7** | `mohammad97okk` | `agw-ACC7-w01` | Sprint 4C | **Persian RTL Dialogue**: Implementing Ren'Py 8.5.3 dialogue trees with `config.rtl = True`. |
| | | `agw-ACC7-w02` | Sprint 4C | **Event Bus Triggers**: Connecting Ren'Py dialogue events to Godot `TBS-M00` Event Bus and `TBS-M02` Player Controller. |
| | | `agw-ACC7-w03` | Sprint 4C | **Composition Root & SQLite**: State persistence for player progress, café orders, and dialogue history. |
| **ACC8** | `moradzahra85-png` | `agw-ACC8-w01` | Sprint 4D | **Vertical Slice Scene Integration**: Assembling all modules (`TBS-M00`..`TBS-M06`) into playable vertical slice. |
| | | `agw-ACC8-w02` | Sprint 4D | **Headless Automated Tests & APK**: Godot 4.3 headless scene runner, Ren'Py lint, and Android APK build verification. |
| | | `agw-ACC8-w03` | Sprint 4D | **QA Transcript Generation**: Generating structured QA logs and gate transcripts for ACC6 Aggregator. |

---

## 4. Aggregator & Quality Gate Architecture (ACC6)

### 4.1 Master Aggregator Role (`ACC6`)
- `mohammadlali0707-stack` (`ACC6`) is **strictly UNTASKED from implementation**.
- Dedicated exclusively to:
  1. `w01`: Harvesting outputs from `Reports/agy/acc{0..8}/*.txt`.
  2. `w02`: Running `python3 Tools/run_gates.py` and `python3 Tools/check_changelog.py`.
  3. `w03`: Publishing unified Fleet Report to `Reports/agy/fleet_report_sprints_1_4.md` and syncing to Notion Card `3f9befc7-ddfb-81ea-b452-e64d1df11f2f`.

### 4.2 Quality Gates Overview
1. **Gate 1 — YAML Lint & Workflow Safety**:
   - CRLF line endings check.
   - YAML syntax and non-empty job definitions.
   - Heredoc backtick escaping check.
   - Job-level context availability (`Tools/check_job_env_contexts.py`).
   - Run injection prevention (`Tools/check_run_injection.py`).
2. **Gate 2 — runs-on Policy**:
   - Protected monitors (`gate-webhook-health.yml`, `gate-runs-on-policy.yml`, `gate-yaml-lint.yml`) strictly enforced on GitHub-hosted (`ubuntu-latest`).
3. **Gate 3 — Runner Dependencies & Schema**:
   - CLI tools verified (`gh`, `git`, `python3`, `curl`, `base64`).
4. **Gate 4 — Changelog Tracking**:
   - `CHANGELOG.md` verifies Sprints 1 to 4 are recorded.
5. **Gate 5 — TBS Asset & Architecture Gate**:
   - Magic bytes verified for JFIF (`\xff\xd8\xff`) and PNG (`\x89PNG\r\n\x1a\n`).
   - Godot 4.3 module roster (`TBS-M00` to `TBS-M06`) verified.
   - Ren'Py RTL Persian configuration (`config.rtl = True`) verified.
6. **Gate 6 — Session Sentinel Self-Test**:
   - Atomic JSON writer and Gemini session health probe validated.
7. **Gate 7 — MCP Telemetry Client**:
   - Dry-run validation of JSON-RPC 2.0 `tools/call` payloads for `append_notion_block` and `send_message_to_cookie`.

---

## 5. Dispatch Directive & Execution Runbook

### Dispatch Directive Command:
```bash
/dispatch --slot all --accounts ACC0,ACC1,ACC2,ACC3,ACC4,ACC5,ACC7,ACC8 --summarizer ACC6 --runners 27
```

### Execution Verification:
```bash
# Verify dispatch directive parsing:
python3 Tools/fleet_dispatcher.py

# Run all repository gates (ACC6-w02):
python3 Tools/run_gates.py

# Verify changelog compliance:
python3 Tools/check_changelog.py

# Run full fleet aggregation and report generation (ACC6-w03):
python3 Tools/fleet_summarizer.py
```
