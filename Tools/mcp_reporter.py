#!/usr/bin/env python3
"""MCP JSON-RPC 2.0 Telemetry Client for AGY Runners.

Implements Protocol '2024-11-05' (mcp_router_v2.js) targeting the n8n MCP Gateway:
Endpoint: https://n8n.airboxvip.top/webhook/mcp

Supports tools/call for:
- append_notion_block: Appends execution status and summary to Notion page/block
- send_message_to_cookie: Dispatches notification to Cookie bot / Telegram bridge
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_MCP_GATEWAY = os.environ.get("MCP_GATEWAY_URL", "https://n8n.airboxvip.top/webhook/mcp")
MCP_PROTOCOL_VERSION = "2024-11-05"


def build_jsonrpc_request(request_id: str, tool_name: str, arguments: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
        },
    }


def send_mcp_request(gateway_url: str, payload: dict, timeout: int = 15) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(gateway_url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-MCP-Protocol-Version", MCP_PROTOCOL_VERSION)
    req.add_header("User-Agent", f"AGY-Runner-MCP-Client/{MCP_PROTOCOL_VERSION}")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            try:
                parsed = json.loads(body)
                return status, parsed
            except Exception:
                return status, body
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", "replace")[:300]
        return e.code, err_body
    except Exception as e:
        return 0, str(e)


def report_execution(
    gateway_url: str,
    issue_number: str = "",
    callback_id: str = "",
    account: str = "",
    tag: str = "",
    target_repo: str = "",
    run_id: str = "",
    status: str = "success",
    message: str = "",
    dry_run: bool = False,
) -> bool:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_id_val = run_id or os.environ.get("GITHUB_RUN_ID", str(int(time.time())))
    acc_val = account or os.environ.get("ACCOUNT", "unknown")
    tag_val = tag or callback_id or f"run-{run_id_val}"

    summary_text = message or f"AGY runner completed {tag_val} (issue #{issue_number}) on ACC{acc_val} with status {status}."

    notion_args = {
        "page_id": "3f9befc7-ddfb-81ea-b452-e64d1df11f2f",
        "block_type": "callout",
        "timestamp": ts,
        "run_id": run_id_val,
        "account": f"ACC{acc_val}" if not acc_val.startswith("ACC") else acc_val,
        "issue_number": issue_number,
        "callback_id": callback_id,
        "tag": tag_val,
        "target_repo": target_repo,
        "status": status,
        "summary": summary_text,
    }

    cookie_args = {
        "recipient": "cookie",
        "timestamp": ts,
        "account": f"ACC{acc_val}" if not acc_val.startswith("ACC") else acc_val,
        "issue": issue_number,
        "status": status,
        "message": f"🤖 [AGY Fleet] {summary_text} (Target: {target_repo or 'agw-workers'})",
    }

    req_notion = build_jsonrpc_request(f"notion-{run_id_val}-{int(time.time())}", "append_notion_block", notion_args)
    req_cookie = build_jsonrpc_request(f"cookie-{run_id_val}-{int(time.time())}", "send_message_to_cookie", cookie_args)

    if dry_run:
        print("[DRY RUN] Notion block request:")
        print(json.dumps(req_notion, indent=2))
        print("[DRY RUN] Cookie message request:")
        print(json.dumps(req_cookie, indent=2))
        return True

    all_ok = True
    print(f"Posting MCP telemetry to {gateway_url}...")

    # 1. Call append_notion_block
    st1, resp1 = send_mcp_request(gateway_url, req_notion)
    if st1 in (200, 201, 204):
        print(f"✅ append_notion_block dispatched successfully (HTTP {st1})")
    else:
        print(f"⚠️ append_notion_block returned HTTP {st1}: {resp1}")
        all_ok = False

    # 2. Call send_message_to_cookie
    st2, resp2 = send_mcp_request(gateway_url, req_cookie)
    if st2 in (200, 201, 204):
        print(f"✅ send_message_to_cookie dispatched successfully (HTTP {st2})")
    else:
        print(f"⚠️ send_message_to_cookie returned HTTP {st2}: {resp2}")
        all_ok = False

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="MCP JSON-RPC 2.0 Runner Telemetry Reporter")
    parser.add_argument("--gateway", default=DEFAULT_MCP_GATEWAY, help="MCP Gateway endpoint URL")
    parser.add_argument("--issue", default="", help="GitHub issue number")
    parser.add_argument("--callback-id", default="", help="Callback / request ID")
    parser.add_argument("--account", default="", help="Account index or identifier (e.g. 0, ACC3)")
    parser.add_argument("--tag", default="", help="Run tag or task tag")
    parser.add_argument("--target-repo", default="", help="Target repository")
    parser.add_argument("--run-id", default="", help="GitHub Run ID")
    parser.add_argument("--status", default="success", help="Execution status (success, failure, completed)")
    parser.add_argument("--message", default="", help="Custom message or summary text")
    parser.add_argument("--dry-run", action="store_true", help="Print JSON-RPC payloads without dispatching")

    args = parser.parse_args()

    # Progress/telemetry reporting should never fail the runner pipeline
    try:
        report_execution(
            gateway_url=args.gateway,
            issue_number=args.issue,
            callback_id=args.callback_id,
            account=args.account,
            tag=args.tag,
            target_repo=args.target_repo,
            run_id=args.run_id,
            status=args.status,
            message=args.message,
            dry_run=args.dry_run,
        )
        return 0
    except Exception as e:
        print(f"::warning::MCP telemetry client failed gracefully: {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
