#!/usr/bin/env python3
"""Register custom PII recognizers with the Presidio Analyzer service.

Usage: python3 register_presidio_recognizers.py <analyzer_url> <recognizers_yml_path>

Called by the Ansible role after the Presidio Analyzer container is healthy.
Reads recognizers from the YAML file and POSTs each one to the analyzer API.
"""

import json
import sys
import urllib.request
import urllib.error

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not available. Install with: pip install pyyaml")
    sys.exit(1)


def register_recognizer(analyzer_url: str, recognizer: dict) -> bool:
    """Register a single pattern recognizer via the Presidio REST API."""
    url = f"{analyzer_url}/recognizers"
    payload = json.dumps(recognizer).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"  OK: {recognizer['name']} (HTTP {resp.status})")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  FAIL: {recognizer['name']} (HTTP {e.code}): {body}")
        return False
    except Exception as e:
        print(f"  FAIL: {recognizer['name']}: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <analyzer_url> <recognizers_yml_path>")
        sys.exit(1)

    analyzer_url = sys.argv[1].rstrip("/")
    recognizers_path = sys.argv[2]

    # Load recognizers from YAML
    try:
        with open(recognizers_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Recognizers file not found: {recognizers_path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR loading recognizers: {e}")
        sys.exit(1)

    recognizers = data.get("recognizers", [])
    if not recognizers:
        print("No recognizers found in YAML file")
        sys.exit(0)

    print(f"Registering {len(recognizers)} custom recognizers at {analyzer_url}...")
    ok = 0
    for rec in recognizers:
        # Convert YAML format to Presidio Analyzer API format
        api_rec = {
            "name": rec["name"],
            "supported_entity": rec["entity_type"],
            "supported_language": rec.get("language", "pt"),
            "patterns": [
                {"name": p["name"], "regex": p["regex"], "score": p["score"]}
                for p in rec.get("patterns", [])
            ],
            "context": rec.get("context_phrases", []),
        }
        if register_recognizer(analyzer_url, api_rec):
            ok += 1

    print(f"Registered {ok}/{len(recognizers)} recognizers")

    if ok == 0 and len(recognizers) > 0:
        print("WARNING: No recognizers were registered successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()
