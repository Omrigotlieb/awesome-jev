#!/usr/bin/env python3
"""Re-audit every GitHub entry in entries.json.

For each repository it fetches the README directly from raw.githubusercontent.com and records:
  link_status : "ok" if the repo still serves a README, "dead" otherwise
  evidence    : "strong"   - names api.typesafe.ai, shows a System One call, or names both TypeSafe and Jev
                "mentions" - names Jev or TypeSafe System One, nothing stronger
                "none"     - live, but the README shows no Jev reference at all
  primitives  : which of Choice / Score / Boolean / Noul the README mentions

Usage:  python3 audit.py [--workers 24]
Then:   python3 build_readme.py
"""
from __future__ import annotations
import json, re, sys, pathlib, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent
BRANCHES = ("main", "master", "HEAD")
FILES = ("README.md", "readme.md", "README.MD", "Readme.md", "README.rst", "README", "docs/README.md")
UA = {"User-Agent": "awesome-jev-audit/1.0"}


def fetch_readme(repo: str) -> str | None:
    for br in BRANCHES:
        for fn in FILES:
            url = f"https://raw.githubusercontent.com/{repo}/{br}/{fn}"
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=15) as r:
                    if r.status == 200:
                        return r.read().decode("utf-8", "ignore")
            except urllib.error.HTTPError:
                continue
            except Exception:
                continue
    return None


def classify(text: str) -> tuple[str, list[str]]:
    low = text.lower()
    api = bool(re.search(r"api\.typesafe\.ai|typesafe\.ai/v1|typesafe\.ai/api", low))
    call = bool(re.search(r"systemone\(|system_one\(|\.systemOne|typesafe\.\w+\(|jev\.(ask|decide|query)", text, re.I))
    jev = bool(re.search(r"\bjev\b", low))
    ts = "typesafe" in low
    s1 = bool(re.search(r"system[\s_-]?one|systemone", low))
    prims = sorted({p for p in ("choice", "score", "boolean", "noul") if re.search(rf"\b{p}\b", low)})
    if api or call or (ts and jev):
        return "strong", prims
    if jev or (ts and s1):
        return "mentions", prims
    return "none", prims


def main() -> None:
    workers = 24
    if "--workers" in sys.argv:
        workers = int(sys.argv[sys.argv.index("--workers") + 1])

    data = json.loads((ROOT / "entries.json").read_text())
    repos = sorted({e["repo"] for e in data["entries"] if e["repo"]})
    print(f"auditing {len(repos)} repositories with {workers} workers")

    results: dict[str, tuple[str, str, list[str]]] = {}

    def work(repo: str) -> None:
        text = fetch_readme(repo)
        if text is None:
            results[repo] = ("dead", "unchecked", [])
        else:
            ev, prims = classify(text)
            results[repo] = ("ok", ev, prims)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(work, repos))

    changed = 0
    for e in data["entries"]:
        if not e["repo"]:
            continue
        status, ev, prims = results[e["repo"]]
        if (e["link_status"], e["evidence"]) != (status, ev):
            changed += 1
            print(f"  changed  {e['repo']:50} {e['link_status']}/{e['evidence']} -> {status}/{ev}")
        e["link_status"], e["evidence"], e["primitives"] = status, ev, prims

    import datetime
    data["meta"]["audited"] = datetime.date.today().isoformat()
    (ROOT / "entries.json").write_text(json.dumps(data, indent=1))

    dead = sum(1 for e in data["entries"] if e["link_status"] == "dead")
    print(f"\ndone: {len(repos)} repos, {dead} dead, {changed} changed. Now run: python3 build_readme.py")


if __name__ == "__main__":
    main()
