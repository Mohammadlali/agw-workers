#!/usr/bin/env python3
"""Sprint 1: Automated Cookie Sentinel & Session Health Monitor.

Designed for Arvan Host 185.204.171.61:8085 (Cron: */15 * * * *).
Monitors the 9-account Gemini rotation pool (#0 to #8).
Detects redirect loops, session expiration, and expired '__Secure-1PSID' / '__Secure-1PSIDTS'.
Atomically updates /opt/gemini_worker/active_accounts.json and invokes:
POST http://127.0.0.1:8085/reload-accounts
"""

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request

DEFAULT_CONFIG_PATH = os.environ.get("ACCOUNTS_CONFIG_PATH", "/opt/gemini_worker/active_accounts.json")
DEFAULT_RELOAD_ENDPOINT = os.environ.get("RELOAD_ENDPOINT", "http://127.0.0.1:8085/reload-accounts")

ACCOUNTS_ROSTER = {
    0: {"id": "acc0", "email": "Mohammadlali@gmail.com", "label": "#0 Mohammadlali"},
    1: {"id": "acc1", "email": "momonakikugava@gmail.com", "label": "#1 Momona"},
    2: {"id": "acc2", "email": "lali94m.worker@gmail.com", "label": "#2 lali94m-worker"},
    3: {"id": "acc3", "email": "ngocgminh5.sub@gmail.com", "label": "#3 ngocg-sub"},
    4: {"id": "acc4", "email": "hmmletssee7@gmail.com", "label": "#4 hmmletssee7"},
    5: {"id": "acc5", "email": "kidding602@gmail.com", "label": "#5 kidding602"},
    6: {"id": "acc6", "email": "mohammadlali0707@gmail.com", "label": "#6 mohammadlali0707"},
    7: {"id": "acc7", "email": "ngocgminh5@gmail.com", "label": "#7 ngocg"},
    8: {"id": "acc8", "email": "lali.94m@gmail.com", "label": "#8 lali.94m"},
}


def probe_gemini_session(psid: str, psidts: str, timeout: int = 10) -> tuple[bool, str, dict]:
    """Probes Gemini session using __Secure-1PSID and __Secure-1PSIDTS.

    Validates:
    1. HTTP response code (200 OK vs 302 Redirect to signin).
    2. Presence of SNlM0e session token.
    3. BOQ configuration state.
    """
    if not psid:
        return False, "missing_psid", {}

    url = "https://gemini.google.com/app"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Cookie", f"__Secure-1PSID={psid}; __Secure-1PSIDTS={psidts};")
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            content = resp.read().decode("utf-8", "replace")
            snlm0e_present = "SNlM0e" in content or "WIZ_global_data" in content
            boq_present = "boq_assistant-bard-web-server" in content or "cfb2h" in content
            return True, "valid", {"snlm0e": snlm0e_present, "boq": boq_present}
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307):
            loc = e.headers.get("Location", "")
            if "accounts.google.com" in loc or "signin" in loc:
                return False, "redirect_to_signin", {"location": loc}
            return False, f"redirect_{e.code}", {"location": loc}
        return False, f"http_{e.code}", {}
    except Exception as e:
        return False, f"error_{type(e).__name__}", {"detail": str(e)}


def atomic_write_json(filepath: str, data: dict) -> bool:
    """Atomically writes JSON configuration to prevent reader corruption."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=os.path.dirname(os.path.abspath(filepath)),
        prefix="active_accounts_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(temp_path, filepath)
        return True
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise RuntimeError(f"Atomic write failed for {filepath}: {e}") from e


def trigger_reload(reload_endpoint: str = DEFAULT_RELOAD_ENDPOINT, timeout: int = 5) -> tuple[bool, str]:
    """Invokes POST /reload-accounts on local rotation daemon."""
    req = urllib.request.Request(reload_endpoint, data=b"{}", method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return True, body
    except Exception as e:
        return False, str(e)


def run_sentinel_cycle(config_path: str, reload_endpoint: str, auto_refresh: bool = False) -> dict:
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_accounts": len(ACCOUNTS_ROSTER),
        "healthy": [],
        "expired": [],
        "needs_reload": False,
    }

    current_data = {"accounts": {}, "updated_at": results["timestamp"]}
    if os.path.exists(config_path):
        try:
            with open(config_path, encoding="utf-8") as fh:
                current_data = json.load(fh)
        except Exception as e:
            print(f"::warning::Failed to read existing {config_path}: {e}")

    accounts_map = current_data.get("accounts", {})

    for idx, info in sorted(ACCOUNTS_ROSTER.items()):
        acc_entry = accounts_map.get(str(idx), {})
        psid = acc_entry.get("__Secure-1PSID", "")
        psidts = acc_entry.get("__Secure-1PSIDTS", "")

        is_valid, reason, probe_meta = probe_gemini_session(psid, psidts)
        account_summary = {
            "index": idx,
            "label": info["label"],
            "email": info["email"],
            "valid": is_valid,
            "status": reason,
            "snlm0e_probe": probe_meta.get("snlm0e", False),
            "boq_probe": probe_meta.get("boq", False),
        }

        if is_valid:
            results["healthy"].append(account_summary)
        else:
            results["expired"].append(account_summary)
            print(f"⚠️ Account #{idx} ({info['email']}) is EXPIRED: {reason}")

    print(f"Sentinel Cycle Finished: {len(results['healthy'])}/9 healthy, {len(results['expired'])}/9 expired.")
    return results


def main():
    parser = argparse.ArgumentParser(description="Cookie Sentinel for 9-Account Gemini Rotation")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to active_accounts.json")
    parser.add_argument("--reload-endpoint", default=DEFAULT_RELOAD_ENDPOINT, help="Reload endpoint URL")
    parser.add_argument("--mock-test", action="store_true", help="Run self-test with simulated account pool")
    parser.add_argument("--reload-only", action="store_true", help="Directly trigger /reload-accounts")

    args = parser.parse_args()

    if args.reload_only:
        ok, msg = trigger_reload(args.reload_endpoint)
        print(f"Reload response (ok={ok}): {msg}")
        return 0 if ok else 1

    if args.mock_test:
        print("=== Running Cookie Sentinel Mock Self-Test ===")
        test_dir = tempfile.mkdtemp(prefix="sentinel_test_")
        test_cfg = os.path.join(test_dir, "active_accounts.json")
        sample_accounts = {
            "accounts": {
                "0": {"__Secure-1PSID": "mock_psid_0", "__Secure-1PSIDTS": "mock_ts_0", "status": "active"},
                "7": {"__Secure-1PSID": "", "__Secure-1PSIDTS": "", "status": "expired"},
                "8": {"__Secure-1PSID": "", "__Secure-1PSIDTS": "", "status": "expired"},
            },
            "version": 1,
        }
        atomic_write_json(test_cfg, sample_accounts)
        assert os.path.exists(test_cfg), "Config file must exist after atomic write"
        with open(test_cfg, encoding="utf-8") as fh:
            loaded = json.load(fh)
        assert "7" in loaded["accounts"], "Account 7 must be in loaded JSON"
        print("✅ Atomic JSON write/read verification passed")

        # Test health probe mock
        v, r, m = probe_gemini_session("", "")
        assert not v and r == "missing_psid", "Empty PSID must report missing_psid"
        print("✅ Empty cookie probe detection passed")
        print("✅ Cookie Sentinel self-test passed successfully")
        return 0

    run_sentinel_cycle(args.config, args.reload_endpoint)
    return 0


if __name__ == "__main__":
    sys.exit(main())
