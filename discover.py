#!/usr/bin/env python3
"""Find Jev projects that are not in the list yet.

Runs GitHub's code/repository search (available inside GitHub Actions via GITHUB_TOKEN,
and to anyone with a token locally). Anything new is added to entries.json in the
`unreviewed` category — never straight into a curated one, because a search hit is a
lead, not a verified entry. A human promotes it by editing its category.

Usage:  GITHUB_TOKEN=... python3 discover.py [--max-new 40]
Then:   python3 audit.py && python3 build_readme.py
"""
from __future__ import annotations
import json, os, re, sys, time, pathlib, urllib.parse, urllib.request, urllib.error, datetime

ROOT = pathlib.Path(__file__).resolve().parent
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

QUERIES = [
    "jev in:name",
    "jev in:description",
    "typesafe jev in:readme",
    '"api.typesafe.ai" in:readme',
    '"system one" jev in:readme',
    "systemone typesafe in:readme",
    '"System One model" in:readme',
    "topic:jev",
    "topic:typesafe-ai",
]

# Repositories whose names look like Jev but are something else entirely.
NAME_NOISE = re.compile(r"\b(jevons|jevelin|jeverson|jevil)\b", re.I)


def api(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "awesome-jev-discover/1.0",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": f"{e.code} {e.reason}"}
    except Exception as e:
        return {"_error": str(e)}


def search() -> dict[str, dict]:
    found: dict[str, dict] = {}
    for q in QUERIES:
        for page in (1, 2):
            url = ("https://api.github.com/search/repositories?"
                   f"q={urllib.parse.quote(q)}&per_page=100&page={page}&sort=updated")
            d = api(url)
            if "_error" in d:
                print(f"  ! {q!r} page {page}: {d['_error']}")
                break
            items = d.get("items") or []
            for it in items:
                found[it["full_name"]] = it
            print(f"  {q!r} page {page}: {len(items)} results (total unique {len(found)})")
            if len(items) < 100:
                break
            time.sleep(2)
        time.sleep(2)
    return found


def looks_like_jev(repo: dict) -> bool:
    blob = " ".join(filter(None, [repo.get("name"), repo.get("description"),
                                  " ".join(repo.get("topics") or [])]))
    if NAME_NOISE.search(blob):
        return False
    return bool(re.search(r"\bjev\b|typesafe|system[ -]?one", blob, re.I))


def main() -> None:
    max_new = 40
    if "--max-new" in sys.argv:
        max_new = int(sys.argv[sys.argv.index("--max-new") + 1])

    data = json.loads((ROOT / "entries.json").read_text())
    known = {e["repo"] for e in data["entries"] if e["repo"]}
    known_urls = {e["url"].lower().rstrip("/") for e in data["entries"]}
    print(f"{len(known)} repositories already listed")

    hits = search()
    candidates = [r for name, r in hits.items()
                  if name not in known
                  and f"https://github.com/{name}".lower() not in known_urls
                  and looks_like_jev(r)
                  and not r.get("archived")]
    candidates.sort(key=lambda r: (-r["stargazers_count"], r["full_name"]))
    candidates = candidates[:max_new]

    if not candidates:
        print("no new candidates")
        return

    today = datetime.date.today().isoformat()
    for r in candidates:
        desc = (r.get("description") or "").strip().rstrip(".")
        if not desc:
            desc = "No description provided by the repository"
        data["entries"].append({
            "name": r["name"],
            "url": r["html_url"],
            "desc": desc + " *(auto-discovered, description not yet written)*",
            "category": "unreviewed",
            "repo": r["full_name"],
            "lists": 0,
            "sources": ["auto-discovery"],
            "link_status": "ok",
            "evidence": "unchecked",
            "primitives": [],
            "extra_links": [],
            "discovered": today,
        })
        print(f"  + {r['full_name']}  ({r['stargazers_count']}*)")

    data["meta"]["last_discovery"] = today
    (ROOT / "entries.json").write_text(json.dumps(data, indent=1))
    print(f"\nadded {len(candidates)} candidates to the unreviewed category")


if __name__ == "__main__":
    main()
