# Changelog

All notable changes to the `agw-workers` repository and fleet swarm are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Comprehensive Software Design Specification (SDD) for Tri-Cluster Sprints 1–4 across 27 AGY Runners.
- Closed-loop MCP telemetry client `Tools/mcp_reporter.py` implementing JSON-RPC 2.0 (Protocol 2024-11-05).
- Unified repository gate runner `Tools/run_gates.py` for ACC6 Aggregator.
- Automated fleet dispatch and summarizer utilities `Tools/fleet_dispatcher.py` and `Tools/fleet_summarizer.py`.

## [Sprint 1] - 2026-10-14 - Headless Automated Session Refresher (185.204.171.61:8085)
### Added
- `Tools/cookie_sentinel.py`: Session health monitoring daemon running on `*/15 * * * *` cron.
- `Tools/headless_session_refresher.py`: Playwright/Chromium automated cookie harvesting for expired accounts #7 (`ngocgminh5@gmail.com`) and #8 (`lali.94m@gmail.com`).
- Atomic JSON updater for `/opt/gemini_worker/active_accounts.json` with zero-downtime hot reload via `POST http://127.0.0.1:8085/reload-accounts`.
- `SNlM0e` session token and `BOQ` configuration health probes for 9/9 rotation pool.

## [Sprint 2] - 2026-10-14 - AI Lead Hunter Auto-Proposal Generator (RdtBCbtFClRbiB8U)
### Added
- `Tools/lead_hunter_proposal.py`: Auto-proposal generation engine using Gemini 4 Argon.
- Telegram VIP lead inline button callback router `[🚀 Send AI Proposal]`.
- Integration with Notion CRM Database `3f9befc7-ddfb-8119-a549-d0934e6e8a12`.
- Safe `Plan: false` guard preventing accidental triggering of fleet batch planning.
- One-click Telegram staging mechanism with inline confirmation keyboards.

## [Sprint 3] - 2026-10-14 - Closed-Loop AGY Runner Reporting (agw-workers → MCP → Notion)
### Added
- Workflow hook integration in `.github/workflows/agw-worker.yml` and `.github/workflows/agy-lead-plan.yml`.
- Standard JSON-RPC 2.0 `tools/call` invocations for `append_notion_block` and `send_message_to_cookie` targeting `https://n8n.airboxvip.top/webhook/mcp`.
- End-to-end synchronization with n8n workflows `9AefIVy4aHRcna2W` and `xzBR15arXeESLvYJ`.

## [Sprint 4] - 2026-10-14 - Claud-Cloud-Project (CCP / TBS) Playable Vertical Slice Integration
### Added
- `Tools/check_tbs_assets.py`: Asset integrity gate verifying JFIF/PNG magic-bytes and SHA-256 hashes for Kaveh 3D turnaround (`zahra_1792003384_image.jpg`), Morad Cyber-Barista sprites, and Parchak Cheese Café 3/3 assets (`TBS-M15` / `488babe2-d9f1-4f48-8b1c-3df7d7ddbbf1`).
- Godot 4.3 modular contract validation (`TBS-M00` through `TBS-M06`).
- Ren'Py 8.5.3 RTL Persian dialogue tree configuration validation (`config.rtl = True`).
