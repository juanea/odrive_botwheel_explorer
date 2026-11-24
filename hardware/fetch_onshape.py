#!/usr/bin/env python3
"""Fetch an Onshape publication assembly as a STEP file using API keys from .env.

Usage:
    python3 hardware/fetch_onshape.py
"""

from __future__ import annotations

import base64
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
OUT_STEP = Path(__file__).resolve().parent / "vendor" / "botwheel_explorer.step"

# ODrive BotWheel Explorer Onshape publication
PUBLICATION_ID = "2921014fe168921e9598967c"
PUBLICATION_WORKSPACE_ID = "2fb0d2823425b7bd58ea4a32"
ITEM_ID = "99fdf1e921bf2247872c36a9"
BASE_URL = "https://cad.onshape.com/api/v6"


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Copy .env.template to .env and add Onshape keys.")
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip("\"'")
    return env


def make_headers(access_key: str, secret_key: str, accept: str = "application/json") -> dict[str, str]:
    token = base64.b64encode(f"{access_key}:{secret_key}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Accept": accept,
        "Content-Type": "application/json",
    }


def api_json(url: str, headers: dict[str, str], body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    env = load_env(ENV_FILE)
    ak = env.get("ONSHAPE_ACCESS_KEY", "")
    sk = env.get("ONSHAPE_SECRET_KEY", "")
    if not ak or not sk:
        print("Error: ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY must be set in .env", file=sys.stderr)
        return 1

    headers = make_headers(ak, sk)

    # 1. Resolve publication item -> (documentId, versionId, elementId)
    pub = api_json(f"{BASE_URL}/publications/{PUBLICATION_ID}/items", headers)
    item = next((i for i in pub.get("items", []) if i.get("id") == ITEM_ID), None)
    if item is None:
        item = next((i for i in pub.get("items", []) if i.get("elementType") == "ASSEMBLY"), None)
    if item is None:
        print("Error: No assembly item found in publication", file=sys.stderr)
        return 1

    did = item["documentId"]
    vid = item["versionId"]
    eid = item["elementId"]
    print(f"Resolved assembly: d/{did}/v/{vid}/e/{eid} ({item.get('versionName', '')})")

    # 2. Start STEP translation (pass linkDocumentId + linkDocumentWorkspaceId for publication access)
    link_qs = f"linkDocumentId={PUBLICATION_ID}&linkDocumentWorkspaceId={PUBLICATION_WORKSPACE_ID}"
    trans_url = f"{BASE_URL}/assemblies/d/{did}/v/{vid}/e/{eid}/translations?{link_qs}"
    payload = {
        "formatName": "STEP",
        "storeInDocument": False,
        "stepVersionString": "AP214",
        "stepUnit": "MILLIMETER",
        "linkDocumentId": PUBLICATION_ID,
        "linkDocumentWorkspaceId": PUBLICATION_WORKSPACE_ID,
    }
    try:
        job = api_json(trans_url, headers, payload)
    except urllib.error.HTTPError as e:
        print(f"Translation POST failed ({e.code}): {e.read().decode()}", file=sys.stderr)
        return 1

    tid = job["id"]
    print(f"Translation started: {tid} (state={job.get('requestState')})")

    # 3. Poll until DONE
    status_url = f"{BASE_URL}/translations/{tid}"
    while True:
        status = api_json(status_url, headers)
        state = status.get("requestState")
        if state == "DONE":
            break
        if state == "FAILED":
            print(f"Translation FAILED: {status.get('failureReason')}", file=sys.stderr)
            return 1
        print(f"  state={state} ...")
        time.sleep(2)

    ext_ids = status.get("resultExternalDataIds") or []
    if not ext_ids:
        print(f"Error: No resultExternalDataIds in {status}", file=sys.stderr)
        return 1

    # 4. Download external data (stored under resultDocumentId, which may be the publication ID)
    ext_id = ext_ids[0]
    res_did = status.get("resultDocumentId") or did
    dl_url = f"{BASE_URL}/documents/d/{res_did}/externaldata/{ext_id}?{link_qs}"
    dl_headers = make_headers(ak, sk, accept="application/octet-stream")
    req = urllib.request.Request(dl_url, headers=dl_headers)
    OUT_STEP.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = resp.read()
    OUT_STEP.write_bytes(data)
    print(f"Saved {OUT_STEP} ({len(data) / (1024 * 1024):.2f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
