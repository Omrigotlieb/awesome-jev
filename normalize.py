#!/usr/bin/env python3
"""Normalise entries.json: merge cross-URL duplicates, disambiguate colliding names.

Two projects listed under two URLs (a GitHub repo and its package page or marketing
site) become one entry, with the secondary URL kept as an extra link. Different
projects that happen to share a name get their owner appended so the list stays
unambiguous.

Usage: python3 normalize.py    (then: python3 build_readme.py)
"""
from __future__ import annotations
import json, collections, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
SECONDARY_HOSTS = ("pypi.org", "npmjs.com", "crates.io", "pkg.go.dev", "rubygems.org",
                   "packagist.org", "marketplace.visualstudio.com", "hex.pm")


def key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def main() -> None:
    data = json.loads((ROOT / "entries.json").read_text())
    E = data["entries"]

    # ---- 1. merge: same project name, one GitHub entry + one non-GitHub entry ----
    by_name: dict[str, list[dict]] = collections.defaultdict(list)
    for e in E:
        by_name[key(e["name"])].append(e)

    merged = 0
    drop: set[int] = set()
    for name, group in by_name.items():
        gh = [e for e in group if e["repo"]]
        non = [e for e in group if not e["repo"]]
        if len(gh) != 1 or not non:
            continue
        primary = gh[0]
        for other in non:
            host = other["url"].split("/")[2] if "://" in other["url"] else ""
            same_project = host.endswith(SECONDARY_HOSTS) or key(other["name"]) == key(primary["name"])
            if not same_project:
                continue
            label = "package" if host.endswith(SECONDARY_HOSTS) else "site"
            if other["url"] not in [u for _, u in primary.get("extra_links", [])]:
                primary.setdefault("extra_links", []).append([label, other["url"]])
            primary["lists"] = max(primary["lists"], other["lists"])
            primary["sources"] = sorted(set(primary["sources"]) | set(other["sources"]))
            if len(other["desc"]) > len(primary["desc"]) * 1.4:
                primary["desc"] = other["desc"]
            drop.add(id(other))
            merged += 1

    E = [e for e in E if id(e) not in drop]

    # ---- 2. disambiguate colliding display names ----
    by_name = collections.defaultdict(list)
    for e in E:
        by_name[key(e["name"])].append(e)
    renamed = 0
    for name, group in by_name.items():
        if len(group) < 2:
            continue
        for e in group:
            if e["repo"]:
                owner = e["repo"].split("/")[0]
                if not e["name"].endswith(")"):
                    e["name"] = f"{e['name']} ({owner})"
                    renamed += 1

    data["entries"] = E
    (ROOT / "entries.json").write_text(json.dumps(data, indent=1))
    print(f"normalised: {merged} duplicate URLs merged, {renamed} names disambiguated, {len(E)} entries remain")


if __name__ == "__main__":
    main()
