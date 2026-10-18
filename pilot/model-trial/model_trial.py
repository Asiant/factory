#!/usr/bin/env python3
"""First model trial harness — discovery item 6 (doc 12 §5).

Probes the Copilot model endpoint(s) under the `model_trial` envelope from
pilot/sandbox/budget-policy.yaml and writes a redacted trial record:

  * catalog probe  (GET /models-style)   -> reachability + auth behaviour
  * one tiny chat completion             -> real inference + usage accounting
  * budget check against the envelope    -> tokens/cost/wall/calls
  * verdict: ok | auth_rejected | network_blocked | budget_exceeded | error

Security rules enforced here:
  * the API key is read from the environment (FACTORY_MODEL_API_TOKEN, then
    GH_TOKEN) and is NEVER written to the record, stdout or the repo
  * response bodies are truncated to a short head before recording
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

HARNESS_VERSION = 1
TRIAL_PROMPT = "Reply with exactly: FACTORY-MODEL-TRIAL-OK"
USER_AGENT = "factory-model-trial/1 (walking-skeleton discovery)"
RESPONSE_HEAD_CHARS = 400

ENDPOINTS = {
    "copilot": {
        "host": "api.githubcopilot.com",
        "role": "primary",
        "base": "https://api.githubcopilot.com",
        "catalog_paths": ["/models"],
        "chat_path": "/chat/completions",
        "headers": {
            "Copilot-Integration-Id": "factory-walking-skeleton",
            "Editor-Plugin-Version": "factory-model-trial/1",
        },
    },
    "models": {
        "host": "models.github.ai",
        "role": "fallback",
        "base": "https://models.github.ai",
        "catalog_paths": ["/inference/models", "/catalog/models"],
        "chat_path": "/inference/chat/completions",
        "headers": {"X-GitHub-Api-Version": "2022-11-28"},
    },
}

FALLBACK_MODEL = "gpt-4o-mini"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_budget(budget_path: Path, envelope_name: str) -> dict:
    policy = yaml.safe_load(budget_path.read_text())
    envelope = policy["envelopes"][envelope_name]
    pricing = policy["pricing"]["notional_rates_usd_per_mtok"]
    return {
        "envelope_name": envelope_name,
        "caps": dict(envelope),
        "rates": dict(pricing),
        "policy_version": policy.get("version"),
    }


def _redact(text: str, token: str | None) -> str:
    if token:
        text = text.replace(token, "[REDACTED]")
    return text[:RESPONSE_HEAD_CHARS]


def _http_request(method: str, url: str, headers: dict, body: dict | None, timeout: int = 15):
    """Returns (status, response_headers, body_text, latency_ms, error)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency = int((time.monotonic() - start) * 1000)
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace"), latency, None
    except urllib.error.HTTPError as exc:
        latency = int((time.monotonic() - start) * 1000)
        try:
            payload = exc.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            payload = ""
        return exc.code, dict(exc.headers or {}), payload, latency, None
    except Exception as exc:  # noqa: BLE001 — network failures are trial data
        latency = int((time.monotonic() - start) * 1000)
        return None, {}, "", latency, f"{type(exc).__name__}: {exc}"


def _classify_attempt(status: int | None, error: str | None, body: str = "", kind: str = "generic") -> str:
    if error is not None:
        return "network-error"
    if status in (401, 403):
        return "auth-rejected"
    if status == 200 and kind in ("catalog", "chat"):
        # 200 alone is not a trial: the body must be a JSON payload of the
        # expected shape (trial-002 found a stub `200 "OK"` front door).
        try:
            parsed = json.loads(body)
        except Exception:  # noqa: BLE001
            return "invalid-response"
        if not isinstance(parsed, dict):
            return "invalid-response"
        if kind == "chat" and not parsed.get("choices"):
            return "invalid-response"
        return "ok"
    if status == 200:
        return "ok"
    return "http-error"


def _run_probe(sources: list[dict], budget: dict, mock: bool) -> dict:
    caps = budget["caps"]
    attempts: list[dict] = []
    tokens_in = tokens_out = 0
    model_used = None
    chat_usage = None

    if mock:
        attempts.append({
            "endpoint": "mock", "op": "mock chat", "outcome": "ok",
            "status": 200, "latency_ms": 1, "error": None,
            "response_head": '{"mock": true, "usage": {"prompt_tokens": 12, "completion_tokens": 4}}',
        })
        tokens_in, tokens_out = 12, 4
        model_used = "mock-model"
        chat_usage = {"prompt_tokens": 12, "completion_tokens": 4, "total_tokens": 16}
        verdict = "mock_ok"
        detail = "harness self-test only — no network, no credential"
    else:
        token = None
        token_env = None
        for env_name in ("FACTORY_MODEL_API_TOKEN", "GH_TOKEN"):
            if os.environ.get(env_name):
                token = os.environ[env_name]
                token_env = env_name
                break

        verdict = "error"
        detail = "no attempt produced a completion"
        for source in sources:
            cfg = ENDPOINTS[source]
            headers = {"User-Agent": USER_AGENT, "Accept": "application/json", **cfg["headers"]}
            if token:
                headers["Authorization"] = f"Bearer {token}"

            catalog_ok = False
            for path in cfg["catalog_paths"]:
                if len(attempts) >= caps["max_model_calls"]:
                    break
                status, _hdrs, body, latency, error = _http_request("GET", cfg["base"] + path, headers, None)
                outcome = _classify_attempt(status, error, body, kind="catalog")
                attempts.append({
                    "endpoint": cfg["host"], "role": cfg["role"], "op": f"catalog GET {path}",
                    "outcome": outcome, "status": status, "latency_ms": latency,
                    "error": _redact(error, token) if error else None,
                    "response_head": _redact(body, token),
                })
                if outcome == "ok":
                    catalog_ok = True
                    try:
                        parsed = json.loads(body)
                        models = parsed.get("data") or parsed.get("models") or parsed.get("id") or []
                        if isinstance(models, list) and models:
                            model_used = models[0].get("id") if isinstance(models[0], dict) else str(models[0])
                        elif isinstance(models, str):
                            model_used = models
                    except Exception:  # noqa: BLE001
                        pass
                    break

            if len(attempts) >= caps["max_model_calls"]:
                break

            status, _hdrs, body, latency, error = _http_request(
                "POST", cfg["base"] + cfg["chat_path"], {**headers, "Content-Type": "application/json"},
                {
                    "model": model_used or FALLBACK_MODEL,
                    "messages": [{"role": "user", "content": TRIAL_PROMPT}],
                    "max_tokens": 16, "temperature": 0, "stream": False,
                },
            )
            outcome = _classify_attempt(status, error, body, kind="chat")
            attempts.append({
                "endpoint": cfg["host"], "role": cfg["role"], "op": f"chat POST {cfg['chat_path']}",
                "outcome": outcome, "status": status, "latency_ms": latency,
                "error": _redact(error, token) if error else None,
                "response_head": _redact(body, token),
            })
            if outcome == "ok":
                try:
                    parsed = json.loads(body)
                    chat_usage = parsed.get("usage") or {}
                    tokens_in = int(chat_usage.get("prompt_tokens") or 0)
                    tokens_out = int(chat_usage.get("completion_tokens") or 0)
                    model_used = parsed.get("model") or model_used
                except Exception:  # noqa: BLE001
                    pass
                verdict = "ok"
                detail = f"chat completion returned 200 via {cfg['host']} (catalog_ok={catalog_ok})"
                break
            if outcome == "auth-rejected" and token:
                verdict = "auth_rejected"
                detail = f"{cfg['host']} reachable; credential from {token_env} rejected (status {status})"
                break
            if outcome == "network-error":
                verdict = "network_blocked"
                detail = f"cannot reach {cfg['host']} from this runner: {error}"
                continue

    cost = (tokens_in * budget["rates"]["input"] + tokens_out * budget["rates"]["output"]) / 1_000_000
    within = (
        (tokens_in + tokens_out) <= caps["max_tokens"]
        and cost <= caps["max_cost_usd"]
        and len(attempts) <= caps["max_model_calls"]
    )
    if verdict == "ok" and not within:
        verdict = "budget_exceeded"

    return {
        "attempts": attempts,
        "usage": {
            "model": model_used,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "tokens_total": tokens_in + tokens_out,
            "chat_usage_raw": chat_usage,
        },
        "cost_usd_notional": round(cost, 6),
        "budget_check": {
            "within_budget": within,
            "tokens": f"{tokens_in + tokens_out}/{caps['max_tokens']}",
            "cost_usd": f"{cost:.6f}/{caps['max_cost_usd']}",
            "model_calls": f"{len(attempts)}/{caps['max_model_calls']}",
        },
        "verdict": verdict,
        "verdict_detail": detail,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-id", required=True, help="e.g. trial-001")
    parser.add_argument("--runner", required=True, choices=["sandbox", "ci", "mock"], help="where the trial runs")
    parser.add_argument("--endpoints", default="copilot", help="comma list of: copilot, models")
    parser.add_argument("--mock", action="store_true", help="harness self-test, no network/credential")
    parser.add_argument("--require-ok", action="store_true", help="exit non-zero unless verdict is ok")
    parser.add_argument("--notes", default="", help="free-text context for the record (no secrets)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    budget = _load_budget(repo_root / "pilot/sandbox/budget-policy.yaml", "model_trial")
    sources = [s.strip() for s in args.endpoints.split(",") if s.strip()]
    for source in sources:
        if source not in ENDPOINTS:
            parser.error(f"unknown endpoint source {source!r}")

    result = _run_probe(sources, budget, mock=args.mock or args.runner == "mock")

    record = {
        "trial": {
            "id": args.trial_id,
            "runner": args.runner,
            "ts_utc": _now(),
            "harness": "pilot/model-trial/model_trial.py",
            "harness_version": HARNESS_VERSION,
            "objective": "First model trial: reachability + auth + one completion under the model_trial budget (discovery item 6)",
        },
        "credential": {
            "source_env": None if args.mock else ("FACTORY_MODEL_API_TOKEN or GH_TOKEN"),
            "rule": "key from the org secret store at run time; value never recorded (doc 12a item 6)",
        },
        "budget": {
            "envelope": budget["envelope_name"],
            "policy_version": budget["policy_version"],
            "caps": budget["caps"],
            "notional_rates_usd_per_mtok": budget["rates"],
        },
        "prompt": TRIAL_PROMPT,
        "endpoints_requested": sources,
        "notes": args.notes,
        **result,
    }

    out_dir = repo_root / "pilot/model-trial/trials"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.trial_id}-{args.runner}.yaml"
    out_path.write_text(
        "# Model trial record — generated by model_trial.py. Contains no credentials.\n"
        + yaml.safe_dump(record, sort_keys=False, allow_unicode=True)
    )

    print(f"trial {args.trial_id} ({args.runner}) verdict={result['verdict']}")
    print(f"  detail: {result['verdict_detail']}")
    print(f"  budget: {result['budget_check']}")
    print(f"  record: {out_path.relative_to(repo_root)}")
    for attempt in result["attempts"]:
        print(f"  - {attempt['endpoint']} {attempt['op']}: {attempt['outcome']} (status={attempt['status']}, {attempt['latency_ms']}ms)")

    if args.require_ok and result["verdict"] not in ("ok", "mock_ok"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
